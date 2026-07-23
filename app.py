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
    <title>QuickSaver HD</title>
    <style>
        body { background-color: #0f172a; font-family: Arial, sans-serif; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; color: #fff; }
        .main-container { width: 100%; max-width: 400px; padding: 15px; box-sizing: border-box; }
        .card { background: #1e293b; padding: 20px; border-radius: 16px; box-shadow: 0 8px 25px rgba(0,0,0,0.6); text-align: center; }
        h2 { color: #38bdf8; margin-bottom: 20px; font-size: 22px; }
        input { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #334155; border-radius: 8px; background: #0f172a; color: #fff; outline: none; box-sizing: border-box; font-size: 14px; }
        .btn-download { background: #0ea5e9; color: white; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 15px; transition: 0.3s; }
        .btn-download:hover { background: #0284c7; }
        
        /* Result Preview Card Styling */
        #resultContainer { margin-top: 20px; display: none; text-align: left; background: #0f172a; padding: 15px; border-radius: 12px; border: 1px solid #334155; }
        .video-title { font-size: 14px; font-weight: bold; color: #f8fafc; margin-bottom: 10px; word-break: break-all; }
        .thumbnail-box { position: relative; width: 100%; border-radius: 8px; overflow: hidden; margin-bottom: 12px; background: #000; }
        .thumbnail-box img { width: 100%; display: block; border-radius: 8px; max-height: 200px; object-fit: cover; }
        
        .action-btn { display: block; width: 100%; text-align: center; padding: 10px; margin-top: 8px; border-radius: 6px; font-weight: bold; text-decoration: none; font-size: 14px; box-sizing: border-box; }
        .btn-thumb { background: #6366f1; color: white; }
        .btn-thumb:hover { background: #4f46e5; }
        .btn-video { background: #22c55e; color: white; }
        .btn-video:hover { background: #16a34a; }
        
        #statusMessage { margin-top: 10px; color: #fbbf24; font-size: 13px; text-align: center; }
    </style>
</head>
<body>
    <div class="main-container">
        <div class="card">
            <h2>QuickSaver HD</h2>
            <input type="text" id="urlInput" placeholder="Yahan video ka link paste karein...">
            <button class="btn-download" onclick="fetchVideo()">Process & Download</button>
            <div id="statusMessage"></div>

            <div id="resultContainer">
                <div class="video-title" id="videoTitle"></div>
                <div class="thumbnail-box">
                    <img id="videoThumb" src="" alt="Thumbnail">
                </div>
                <a id="thumbDownloadBtn" class="action-btn btn-thumb" href="#" target="_blank" download="thumbnail.jpg">🖼️ Download Thumbnail</a>
                <a id="videoDownloadBtn" class="action-btn btn-video" href="#" target="_blank" download="video.mp4">📥 Direct Video Download Karein</a>
            </div>
        </div>
    </div>

    <script>
    async function fetchVideo() {
        var url = document.getElementById('urlInput').value.trim();
        var statusDiv = document.getElementById('statusMessage');
        var resultContainer = document.getElementById('resultContainer');
        
        if(url === "") { alert("Pehle link dalein!"); return; }
        
        statusDiv.innerHTML = "Video fetch ho rahi hai, thoda intezaar karein...";
        resultContainer.style.display = "none";
        
        try {
            let response = await fetch('/get-video', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url })
            });
            let data = await response.json();
            
            if (data.success) {
                statusDiv.innerHTML = "";
                document.getElementById('videoTitle').innerText = data.title;
                document.getElementById('videoThumb').src = data.thumbnail;
                document.getElementById('thumbDownloadBtn').href = data.thumbnail;
                document.getElementById('videoDownloadBtn').href = data.download_url;
                resultContainer.style.display = "block";
            } else {
                statusDiv.innerHTML = "Error: " + data.message;
            }
        } catch (err) {
            statusDiv.innerHTML = "Kuch galat ho gaya. Dobara koshish karein.";
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
        ydl_opts = {
            'format': 'best',
            'noplaylist': True,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            download_url = info.get('url')
            
            if not download_url and 'formats' in info:
                formats = info.get('formats', [])
                for f in formats:
                    if f.get('url') and f.get('vcodec') != 'none':
                        download_url = f.get('url')
            
            title = info.get('title', 'Downloaded Video')
            thumbnail = info.get('thumbnail', '')
            
            if download_url:
                return jsonify({
                    'success': True, 
                    'download_url': download_url,
                    'title': title,
                    'thumbnail': thumbnail
                })
            else:
                return jsonify({'success': False, 'message': 'Is link ka direct video link nahi mila.'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Invalid link ya yeh website supported nahi hai.'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
