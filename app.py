import os
import requests
import base64
import json
from flask import Flask, jsonify
from Crypto.Cipher import AES

app = Flask(__name__)

# ইউনিভার্সাল ডিক্রিপশন মেথড
def decrypt_any_file(full_target_url):
    secret_key = os.environ.get("AES_KEY", "UC7aw51AjnDYjkFw")
    secret_iv = os.environ.get("AES_IV", "DeEwhulLVbtIGsYS")
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
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
        
        # যদি ডাটাটি JSON ফরম্যাটের হয় তবে অবজেক্ট করবে, নাহলে র টেক্সট
        try:
            return json.loads(clean_json)
        except:
            return clean_json
            
    except Exception as e:
        return {"error": "Decryption Failed", "details": str(e)}

# ফিক্সড রাউট ১: eventCats.txt
@app.route('/event-cats')
def event_cats():
    url = "https://ghdnewhsjsnb9.top/eventCats.txt"
    return jsonify(decrypt_any_file(url))

# ফিক্সড রাউট ২: app.txt
@app.route('/app-config')
def app_config():
    url = "https://ghdnewhsjsnb9.top/app.txt"
    return jsonify(decrypt_any_file(url))

# 🚀 ম্যাজিক রাউট: ফাইলের নাম যাই হোক, ফোল্ডারসহ বা ছাড়া—সব ডাইনামিকালি ডিক্রিপ্ট করবে
@app.route('/get-data/<path:filename>')
def get_dynamic_data(filename):
    base_domain = "https://ghdnewhsjsnb9.top/"
    full_url = f"{base_domain}{filename}"
    
    data = decrypt_any_file(full_url)
    if isinstance(data, dict) and "error" in data:
        return jsonify(data), 404
    return jsonify(data) if isinstance(data, (dict, list)) else data

@app.route('/')
def home():
    return jsonify({
        "status": "Server is Running Dynamically & Perfectly",
        "author": "Ratul",
        "usage": "Use /get-data/FILENAME.txt to decrypt any file.",
        "quick_links": {
            "Event Categories": "/event-cats",
            "App Config": "/app-config",
            "Live Events Example": "/get-data/live-events.txt",
            "Match Stream Example": "/get-data/international-friendly4.txt"
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
