import os
import requests
import base64
import json
from flask import Flask, jsonify, Response
from Crypto.Cipher import AES
from dotenv import load_dotenv

# 🟢 লোকাল টেস্টের জন্য .env ফাইল লোড করবে, Railway-তে ক্লাউড ভেরিয়েবল থেকে সরাসরি রিড করবে
load_dotenv()

app = Flask(__name__)

# =======================================================
# 🛑 সিকিউরড কনফিগারেশন: কোনো আসল ভ্যালু বা চাবি কোডে নেই!
# =======================================================
SECRET_KEY = os.getenv("AES_KEY")
SECRET_IV = os.getenv("AES_IV")
BASE_CHANNEL_URL = os.getenv("BASE_CHANNEL_URL") # যেমন: https://ghdnewhsjsnb9.top/channels/

# ভেরিয়েবল চেক করার সেফটি গার্ড
if not all([SECRET_KEY, SECRET_IV, BASE_CHANNEL_URL]):
    print("❌ CRITICAL ERROR: Environment Variables missing in .env or Railway!")
    exit(1)

# ডাইনামিক বেস ডোমেইন এক্সট্র্যাকশন (channels/ অংশটি বাদ দিয়ে মূল ডোমেইন বের করা)
# এটি স্ল্যাশ (/) সংক্রান্ত যেকোনো এরর অটোমেটিক হ্যান্ডেল করবে
if "channels/" in BASE_CHANNEL_URL:
    BASE_DOMAIN = BASE_CHANNEL_URL.split("channels/")[0]
else:
    BASE_DOMAIN = BASE_CHANNEL_URL if BASE_CHANNEL_URL.endswith("/") else f"{BASE_CHANNEL_URL}/"

# AES ডিক্রিপশনের জন্য সিক্রেট কী এবং আইভি-কে বাইট-এ কনভার্ট করে নেওয়া
KEY_BYTES = SECRET_KEY.encode('utf-8')
IV_BYTES = SECRET_IV.encode('utf-8')

# ইউনিভার্সাল ডিক্রিপশন মেথড
def decrypt_any_file(full_target_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    try:
        response = requests.get(full_target_url, headers=headers, timeout=12)
        if response.status_code != 200:
            return {"error": "Match File Not Found on Main Server", "status_code": response.status_code}
            
        encrypted_text = response.text.strip()
        
        # ক্লাউড ভেরিয়েবল থেকে আসা বাইট কী ব্যবহার করে ডিক্রিপশন করা হচ্ছে
        cipher = AES.new(KEY_BYTES, AES.MODE_CBC, IV_BYTES)
        encrypted_bytes = base64.b64decode(encrypted_text)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        
        padding_len = decrypted_bytes[-1]
        clean_json = decrypted_bytes[:-padding_len].decode('utf-8')
        
        return clean_json
            
    except Exception as e:
        return json.dumps({"error": "Decryption Failed", "details": str(e)})

# রেসপন্স হ্যান্ডেলার (JSON বা প্লেইন টেক্সট দুইটাই সুন্দরভাবে হ্যান্ডেল করবে)
def make_web_response(raw_data):
    if isinstance(raw_data, dict) and "error" in raw_data:
        return jsonify(raw_data), 404
    try:
        json_object = json.loads(raw_data)
        return jsonify(json_object)
    except:
        return Response(raw_data, mimetype='text/plain')

# ফিক্সড রাউট ১: eventCats.txt
@app.route('/event-cats')
def event_cats():
    url = f"{BASE_DOMAIN}eventCats.txt"
    return make_web_response(decrypt_any_file(url))

# ফিক্সড রাউট ২: app.txt
@app.route('/app-config')
def app_config():
    url = f"{BASE_DOMAIN}app.txt"
    return make_web_response(decrypt_any_file(url))

# 🚀 ম্যাজিক রাউট: যেকোনো ম্যাচের স্লাগ ফাইল ডাইনামিকালি ডিক্রিপ্ট করার জন্য
@app.route('/get-data/<path:filename>')
def get_dynamic_data(filename):
    # যদি রিকোয়েস্টে শুরুতে channels/ সহ স্লাগ আসে, তবে তা ক্লিন করে নেওয়া
    clean_filename = filename.replace("channels/", "")
    full_url = f"{BASE_DOMAIN}{clean_filename}"
    return make_web_response(decrypt_any_file(full_url))

@app.route('/')
def home():
    return jsonify({
        "status": "Automation API Server is Running Perfectly",
        "author": "Ratul",
        "usage": "/get-data/SLUG.txt",
        "example": "/get-data/live14-teri.txt",
        "cached_domain_bridge": BASE_DOMAIN
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
