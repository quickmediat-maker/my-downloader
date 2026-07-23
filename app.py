from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Downloader</title>
    <style>
        body { background-color: #0d1b2a; font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #1b263b; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); width: 320px; text-align: center; }
        h2 { color: #48cae4; margin-bottom: 20px; }
        input { width: 90%; padding: 10px; margin-bottom: 15px; border: 1px solid #415a77; border-radius: 6px; background: #0d1b2a; color: #fff; outline: none; }
        button { background: #00b4d8; color: white; border: none; padding: 10px 15px; width: 100%; border-radius: 6px; font-weight: bold; cursor: pointer; }
        button:hover { background: #0096c7; }
        #statusMessage { margin-top: 15px; color: #ffb703; font-size: 14px; word-break: break-all; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Video Downloader</h2>
        <input type="text" id="urlInput" placeholder="Yahan link dalein...">
        <button onclick="fetchVideo()">Download Karein</button>
        <div id="statusMessage"></div>
    </div>
    <script>
    async function fetchVideo() {
        var url = document.getElementById('urlInput').value.trim();
        var statusDiv = document.getElementById('statusMessage');
        if(url === "") { alert("Pehle link dalein!"); return; }
        statusDiv.innerHTML = "Video fetch ho rahi hai...";
        try {
            let response = await fetch('/get-video', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url })
            });
            let data = await response.json();
            if (data.success) {
                statusDiv.innerHTML = '<b>Taiyar hai!</b><br><a href="' + data.download_url + '" target="_blank" download="video.mp4" style="color: #fff; background: #28a745; padding: 8px 15px; display: inline-block; margin-top: 5px; border-radius: 5px; text-decoration: none;">Download Karein</a>';
            } else {
                statusDiv.innerHTML = "Error: " + data.message;
            }
        } catch (err) {
            statusDiv.innerHTML = "Kuch galat ho gaya.";
        }
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML_PAGE

@app.route('/get-video', methods=['POST'])
def get_video():
    data = request.get_json()
    video_url = data.get('url')
    if not video_url:
        return jsonify({'success': False, 'message': 'URL nahi mila'})
    try:
        # YouTube, Instagram aur anya sites ke liye versatile options
        ydl_opts = {
            'format': 'best/bestvideo+bestaudio/best',
            'noplaylist': True,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            download_url = info.get('url')
            
            # Agar direct url nahi milta toh formats me se best uthayenge
            if not download_url and 'formats' in info:
                formats = info.get('formats', [])
                for f in reversed(formats):
                    if f.get('url') and f.get('vcodec') != 'none':
                        download_url = f.get('url')
                        break
            
            if download_url:
                return jsonify({'success': True, 'download_url': download_url})
            else:
                return jsonify({'success': False, 'message': 'Download link nahi nikal paya'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Link invalid hai ya format support nahi hai.'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
