import os
import requests
from flask import Flask, request, Response

app = Flask(__name__)

# 🟢 1. HOME ROUTE (Check Server Status)
@app.route('/')
def home():
    return "🚀 HellfireDevs Proxy Server is Running 24/7!"

# 📺 2. MAIN DYNAMIC STREAM ROUTE (For Music Bot)
@app.route('/stream')
def proxy_tv():
    # Bot jo link bhejega, ye usko catch karega
    target_url = request.args.get('url')
    
    if not target_url:
        return "Bhai, koi URL nahi mila!", 400
        
    # Fake Chrome Browser Identity
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    
    try:
        # Target channel ko Chrome ban kar request bhejega
        req = requests.get(target_url, headers=headers, stream=True)
        
        # Stream ko bot ki taraf relay kar dega
        return Response(
            req.iter_content(chunk_size=1024), 
            content_type=req.headers.get('content-type', 'application/vnd.apple.mpegurl')
        )
    except Exception as e:
        return str(e), 500

# 🛠️ 3. TEST ENDPOINT (Live Web Player)
@app.route('/test')
def test_player():
    # Testing ke liye hum Aaj Tak ka original link proxy ke through bhejenge
    test_url = "/stream?url=https://feeds.intoday.in/aajtak/api/master.m3u8"
    
    # Ek chhota sa HTML player (HLS.js) jo browser mein m3u8 play karega
    html_page = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>HellfireDevs Stream Test</title>
        <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="background-color: #111; color: white; text-align: center; font-family: sans-serif;">
        <h2>📺 HellfireDevs Proxy Test</h2>
        <p>Agar niche video chal rahi hai, toh proxy 100% working hai!</p>
        
        <video id="video" controls autoplay style="width: 90%; max-width: 600px; border: 2px solid red; border-radius: 10px;"></video>
        
        <script>
            var video = document.getElementById('video');
            var videoSrc = '{test_url}';
            
            if (Hls.isSupported()) {{
                var hls = new Hls();
                hls.loadSource(videoSrc);
                hls.attachMedia(video);
                hls.on(Hls.Events.MANIFEST_PARSED, function() {{
                    video.play();
                }});
            }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                video.src = videoSrc;
                video.addEventListener('loadedmetadata', function() {{
                    video.play();
                }});
            }}
        </script>
    </body>
    </html>
    """
    return html_page

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
  
