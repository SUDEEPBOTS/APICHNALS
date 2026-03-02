import os
import requests
import urllib.parse
from urllib.parse import urljoin
from flask import Flask, request, Response

app = Flask(__name__)

# 🟢 1. HOME ROUTE
@app.route('/')
def home():
    return "🚀 HellfireDevs Proxy Server is Running 24/7!"

# 📺 2. MAIN DYNAMIC STREAM ROUTE (Ultimate M3U8 Rewriter)
@app.route('/stream')
def proxy_tv():
    target_url = request.args.get('url')
    
    if not target_url:
        return "Bhai, koi URL nahi mila!", 400
        
    # Extra Security Headers added
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://aajtak.in/",
        "Origin": "https://aajtak.in/"
    }
    
    try:
        req = requests.get(target_url, headers=headers)
        content_type = req.headers.get('content-type', '')

        # 🔥 SMART REWRITER LOGIC 🔥
        # Agar ye m3u8 playlist hai, toh iske andar ke links ko wapas Heroku proxy mein wrap karenge
        if "m3u8" in target_url.lower() or "mpegurl" in content_type.lower() or req.text.startswith("#EXTM3U"):
            lines = req.text.splitlines()
            new_lines = []
            
            # Apne server ka main base URL nikal rahe hain (e.g., https://apiinews...herokuapp.com)
            host_url = request.host_url.rstrip('/').replace("http://", "https://")
            
            
            for line in lines:
                # Agar line comment (#) nahi hai aur khali nahi hai, toh wo ek link hai
                if line.strip() and not line.startswith("#"):
                    # 1. Poora (absolute) link nikalo Akamai/Aaj Tak ka
                    abs_url = urljoin(target_url, line.strip())
                    # 2. Usko encode karo taaki proxy link mein fit baith sake
                    safe_url = urllib.parse.quote(abs_url, safe='')
                    # 3. Us Akamai link ko wapas apne proxy URL ke andar daal do!
                    proxy_url = f"{host_url}/stream?url={safe_url}"
                    new_lines.append(proxy_url)
                else:
                    new_lines.append(line)
                    
            modified_m3u8 = "\n".join(new_lines)
            return Response(modified_m3u8, content_type="application/vnd.apple.mpegurl")
            
        # Agar direct TS chunk ya koi aur media hai, toh seedha Aaj Tak se utha kar FFMPEG ko dedo
        return Response(req.iter_content(chunk_size=1024), content_type=content_type)
        
    except Exception as e:
        return str(e), 500

# 🛠️ 3. TEST ENDPOINT
@app.route('/test')
def test_player():
    test_url = "/stream?url=https%3A%2F%2Ffeeds.intoday.in%2Faajtak%2Fapi%2Fmaster.m3u8"
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
                hls.on(Hls.Events.MANIFEST_PARSED, function() {{ video.play(); }});
            }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                video.src = videoSrc;
                video.addEventListener('loadedmetadata', function() {{ video.play(); }});
            }}
        </script>
    </body>
    </html>
    """
    return html_page

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
