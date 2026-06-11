import os
import requests
import base64
import json
from flask import Flask, jsonify, Response
from Crypto.Cipher import AES

app = Flask(__name__)

# ইউনিভার্সাল ডিক্রিপশন মেথড
def decrypt_any_file(full_target_url):
    secret_key = os.environ.get("AES_KEY", "UC7aw51AjnDYjkFw")
    secret_iv = os.environ.get("AES_IV", "DeEwhulLVbtIGsYS")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(full_target_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return {"error": "File Not Found on Main Server", "status_code": response.status_code}
            
        encrypted_text = response.text.strip()
        
        # কী এবং আইভি-কে বাইট-এ রূপান্তর
        key = secret_key.encode('utf-8')
        iv = secret_iv.encode('utf-8')
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
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
        # ডাটা যদি অলরেডি ভ্যালিড JSON স্ট্রিং হয়
        json_object = json.loads(raw_data)
        return jsonify(json_object)
    except:
        # ডাটা যদি প্লেইন টেক্সট বা ডিক্রিপ্ট হওয়া হিজিবিজি স্ট্রিং হয়
        return Response(raw_data, mimetype='text/plain')

# ফিক্সড রাউট ১: eventCats.txt
@app.route('/event-cats')
def event_cats():
    url = "https://ghdnewhsjsnb9.top/eventCats.txt"
    return make_web_response(decrypt_any_file(url))

# ফিক্সড রাউট ২: app.txt
@app.route('/app-config')
def app_config():
    url = "https://ghdnewhsjsnb9.top/app.txt"
    return make_web_response(decrypt_any_file(url))

# ডাইনামিক রাউট: যেকোনো ফাইলের জন্য
@app.route('/get-data/<path:filename>')
def get_dynamic_data(filename):
    base_domain = "https://ghdnewhsjsnb9.top/"
    full_url = f"{base_domain}{filename}"
    return make_web_response(decrypt_any_file(full_url))

@app.route('/')
def home():
    return jsonify({
        "status": "Server is Running Smoothly",
        "author": "Ratul",
        "endpoints": {
            "Event Categories": "/event-cats",
            "App Config": "/app-config",
            "Dynamic Fetch Example": "/get-data/international-friendly4.txt"
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
