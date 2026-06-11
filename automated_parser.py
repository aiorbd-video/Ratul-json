import re
import json

def parse_live_stream_data(raw_decrypted_json):
    try:
        data = json.loads(raw_decrypted_json)
        extracted_streams = []
        
        # streamUrls এর ভেতর থেকে সব লাইভ লিঙ্ক এবং DRM চাবি আলাদা করা
        if "streamUrls" in data:
            for stream in data["streamUrls"]:
                stream_info = {
                    "channel_name": stream.get("title"),
                    "stream_url": stream.get("link"),
                    "drm_key": stream.get("api"),  # ClearKey (KID:KEY)
                    "type": "DASH (.mpd)" if stream.get("type") == "1" else "HLS (.m3u8)"
                }
                extracted_streams.append(stream_info)
                
        return extracted_streams
    except Exception as e:
        return {"error": "Parsing failed", "details": str(e)}

# উদাহরণ স্বরূপ আপনার লগের ডাটা পাস করে টেস্ট করা
raw_log_data = """{"streamUrls":[{"title":"SporTV BR - AQ","link":"https://a151aivottlinear-a.akamaihd.net/OTTB/sin-nitro/live/dash/enc/m7duvnk2bu/out/v1/d1ad69118b5647309b1eb7213affdb3d/cenc.mpd","api":"4bbcff3289d457b4dd5dbdd21221de9a:c4906b9a9f8dda3c0725bddb8c497733","type":"1"}]}"""

parsed_output = parse_live_stream_data(raw_log_data)
print(json.dumps(parsed_output, indent=4))
