import os
import requests
import base64
import json
from flask import Flask, jsonify
from Crypto.Cipher import AES

app = Flask(__name__)

# ডিক্রিপশন করার মেইন মেথড (ভেরিয়েবল থেকে ডাটা রিড করবে)
def decrypt_server_file(file_path_env_name):
    # এনভায়রনমেন্ট ভেরিয়েবল থেকে আসল ইউআরএল, কী এবং আইভি তুলে আনা হচ্ছে
    target_url = os.environ.get(file_path_env_name)
    secret_key = os.environ.get("AES_KEY")
    secret_iv = os.environ.get("AES_IV")
    
    if not target_url or not secret_key or not secret_iv:
        return {"error": "Missing Configuration", "details": "Environment variables are not configured properly."}
    
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
        return {"error": f"Failed to decrypt requested file", "details": str(e)}

# ১ নম্বর ইউআরএল: live-events ডাটার জন্য
@app.route('/live-events')
def live_events():
    data = decrypt_server_file("URL_LIVE_EVENTS")
    if isinstance(data, dict) and "error" in data:
        return jsonify(data), 500
    return jsonify(data) if isinstance(data, (dict, list)) else data

# ২ নম্বর ইউআরএল: eventCats ডাটার জন্য
@app.route('/event-cats')
def event_cats():
    data = decrypt_server_file("URL_EVENT_CATS")
    if isinstance(data, dict) and "error" in data:
        return jsonify(data), 500
    return jsonify(data) if isinstance(data, (dict, list)) else data

# ৩ নম্বর ইউআরএল: app-config ডাটার জন্য
@app.route('/app-config')
def app_config():
    data = decrypt_server_file("URL_APP_CONFIG")
    if isinstance(data, dict) and "error" in data:
        return jsonify(data), 500
    return jsonify(data) if isinstance(data, (dict, list)) else data

@app.route('/')
def home():
    return jsonify({
        "status": "Server is Running securely",
        "endpoints": {
            "Live Events Data": "/live-events",
            "Event Categories Data": "/event-cats",
            "App Configuration Data": "/app-config"
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
