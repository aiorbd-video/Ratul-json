import os
import requests
import base64
import json
from flask import Flask, jsonify
from Crypto.Cipher import AES

app = Flask(__name__)

# কমন ডিক্রিপশন মেثড
def decrypt_server_file(file_path_env_name):
    target_url = os.environ.get(file_path_env_name)
    secret_key = os.environ.get("AES_KEY")
    secret_iv = os.environ.get("AES_IV")
    
    # ভেরিয়েবল মিসিং থাকলে এরর হ্যান্ডেলিং
    if not target_url or not secret_key or not secret_iv:
        return {"error": "Configuration Missing", "details": f"Please set {file_path_env_name}, AES_KEY, and AES_IV in Env."}
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(target_url, headers=headers, timeout=10)
        encrypted_text = response.text.strip()
        
        # স্ট্রিং কী এবং আইভি-কে বাইট-এ রূপান্তর
        key = secret_key.encode('utf-8')
        iv = secret_iv.encode('utf-8')
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_bytes = base64.b64decode(encrypted_text)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        
        padding_len = decrypted_bytes[-1]
        clean_json = decrypted_bytes[:-padding_len].decode('utf-8')
        
        try:
            return json.loads(clean_json)
        except:
            return clean_json
            
    except Exception as e:
        return {"error": "Decryption Failed", "details": str(e)}

# ১ নম্বর এন্ডপয়েন্ট: live-events ডাটার জন্য
@app.route('/live-events')
def live_events():
    data = decrypt_server_file("URL_LIVE_EVENTS")
    if isinstance(data, dict) and "error" in data:
        return jsonify(data), 500
    return jsonify(data) if isinstance(data, (dict, list)) else data

# ২ নম্বর এন্ডপয়েন্ট: event-cats ডাটার জন্য
@app.route('/event-cats')
def event_cats():
    data = decrypt_server_file("URL_EVENT_CATS")
    if isinstance(data, dict) and "error" in data:
        return jsonify(data), 500
    return jsonify(data) if isinstance(data, (dict, list)) else data

# ৩ নম্বর এন্ডপয়েন্ট: app-config ডাটার জন্য
@app.route('/app-config')
def app_config():
    data = decrypt_server_file("URL_APP_CONFIG")
    if isinstance(data, dict) and "error" in data:
        return jsonify(data), 500
    return jsonify(data) if isinstance(data, (dict, list)) else data

# ৪ নম্বর নতুন এন্ডপয়েন্ট: আপনার ৪র্থ লিংকের জন্য (যেমন: চ্যানেলস বা অন্য কিছু)
@app.route('/channels')
def channels():
    data = decrypt_server_file("URL_FOURTH_LINK")
    if isinstance(data, dict) and "error" in data:
        return jsonify(data), 500
    return jsonify(data) if isinstance(data, (dict, list)) else data

# হোম পেজ রুট (মেইন ডোমেইনে ঢুকলে যা দেখাবে)
@app.route('/')
def home():
    return jsonify({
        "status": "Server is Running Securely",
        "author": "Ratul",
        "endpoints": {
            "Live Events": "/live-events",
            "Event Categories": "/event-cats",
            "App Configuration": "/app-config",
            "Channels/Extra Data": "/channels"
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
