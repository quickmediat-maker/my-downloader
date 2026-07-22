from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Direct HTML page jo seedha browser mein dikhega
HTML_PAGE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Downloader</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: Arial, sans-serif; }
        body { background-color: #0f172a; color: #ffffff; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .container { background-color: #1e293b; padding: 24px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); width: 90%; max-width: 400px; text-align: center; }
        h2 { color: #38bdf8; margin-bottom: 20px; }
        input[type="text"] { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #475569; border-radius: 6px; background-color: #0f172a; color: #fff; font-size: 14px; outline: none; }
        button { width: 100%; padding: 12px; background-color: #38bdf8; border: none; border-radius: 6px; color: #0f172a; font-weight: bold; font-size: 16px; cursor: pointer; }
        button:hover { background-color: #0ea5e9; }
        #statusMessage { margin-top: 15px; font-size: 14px; word-break: break-all; }
        .loading { color: #38bdf8; }
        .success { color: #22c55e; }
        .error { color: #ef4444; }
        a.download-link { display: inline-block; margin-top: 10px; padding: 8px 16px; background-color: #22c55e; color: white; text-decoration: none; border-radius: 4px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Video Downloader</h2>
        <input type="text" id="urlInput" placeholder="Yahan video ka link paste karein...">
        <button onclick="fetchVideo()">Download Karein</button>
        <div id="statusMessage"></div>
    </div>
    <script>
        async function fetchVideo() {
            var url = document.getElementById('urlInput').value.trim();
            var statusDiv = document.getElementById('statusMessage');
            if(url === "") { alert("Pehle link dalein!"); return; }
            statusDiv.className = "loading";
            statusDiv.innerHTML = "Video fetch ho rahi hai...";
            try {
                let response = await fetch('/get-video', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                let data = await response.json();
                if(data.success) {
                    statusDiv.className = "success";
                    statusDiv.innerHTML = `<b>Taiyar hai!</b><br><a class="download-link" href="${data.download_url}" target="_blank">Download Karein</a>`;
                } else {
                    statusDiv.className = code = "error";
                    statusDiv.innerHTML = "Error: " + data.message;
                }
            } catch (err) {
                statusDiv.className = "error";
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
        ydl_opts = {'format': 'best'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            download_url = info.get('url')
            if not download_url and 'formats' in info:
                download_url = info['formats'][-1].get('url')
            if download_url:
                return jsonify({'success': True, 'download_url': download_url})
            else:
                return jsonify({'success': False, 'message': 'Link nahi nikal paya'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
