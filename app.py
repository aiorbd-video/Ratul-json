import os
import requests
import base64
import json
from flask import Flask, jsonify
from Crypto.Cipher import AES

app = Flask(__name__)

# ডিক্রিপশন করার মেইন মেথড (কমন ফাংশন)
def decrypt_server_file(file_name):
    base_url = f"https://ghdnewhsjsnb9.top/{file_name}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        encrypted_text = response.text.strip()
        
        # আমাদের উদ্ধার করা মাস্টার কী এবং আইভি
        key = b"UC7aw51AjnDYjkFw"
        iv = b"DeEwhulLVbtIGsYS"
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_bytes = base64.b64decode(encrypted_text)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        
        padding_len = decrypted_bytes[-1]
        clean_json = decrypted_bytes[:-padding_len].decode('utf-8')
        
        # ডাটাটি যদি JSON ফরম্যাটের হয় তবে অবজেক্ট রিটার্ন করবে, নাহলে ডিরেক্ট প্লেইন টেক্সট
        try:
            return json.loads(clean_json)
        except:
            return clean_json
            
    except Exception as e:
        return {"error": f"Failed to decrypt {file_name}", "details": str(e)}

# ১ নম্বর ইউআরএল: categories/live-events.txt এর জন্য
@app.route('/live-events')
def live_events():
    # যেহেতু এটি একটি ফোল্ডারের ভেতরে, তাই পাথসহ পাস করলাম
    data = decrypt_server_file("categories/live-events.txt")
    if isinstance(data, dict) and "error" in data:
        return jsonify(data), 500
    return jsonify(data) if isinstance(data, (dict, list)) else data

# ২ নম্বর ইউআরএল: eventCats.txt এর জন্য
@app.route('/event-cats')
def event_cats():
    data = decrypt_server_file("eventCats.txt")
    if isinstance(data, dict) and "error" in data:
        return jsonify(data), 500
    return jsonify(data) if isinstance(data, (dict, list)) else data

# ৩ নম্বর ইউআরএল: app.txt এর জন্য
@app.route('/app-config')
def app_config():
    data = decrypt_server_file("app.txt")
    if isinstance(data, dict) and "error" in data:
        return jsonify(data), 500
    return jsonify(data) if isinstance(data, (dict, list)) else data

# হোম পেজ রুট (কোনো পাথ না দিলে যা দেখাবে)
@app.route('/')
def home():
    return jsonify({
        "status": "Server is Running",
        "endpoints": {
            "Live Events Data": "/live-events",
            "Event Categories Data": "/event-cats",
            "App Configuration Data": "/app-config"
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
