from flask import Flask, request, jsonify, render_template_string
import yt_dlp
import json

app = Flask(__name__)

def get_transcript(url):
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'subtitlesformat': 'json3',
        'quiet': True,
        'no_warnings': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        if 'subtitles' in info and 'en' in info['subtitles']:
            sub_url = info['subtitles']['en'][0]['url']
        elif 'automatic_captions' in info and 'en' in info['automatic_captions']:
            sub_url = info['automatic_captions']['en'][0]['url']
        else:
            raise Exception("No English captions available")
        
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl2:
            sub_data = ydl2.urlopen(sub_url).read().decode('utf-8')
            sub_json = json.loads(sub_data)
            
            sentences = []
            current = []
            
            for event in sub_json['events']:
                if 'segs' in event:
                    for seg in event['segs']:
                        if 'utf8' in seg:
                            text = seg['utf8'].strip()
                            if text:
                                current.append(text)
                                if text.endswith(('.', '?', '!')):
                                    sentences.append(' '.join(current))
                                    current = []
            
            if current:
                sentences.append(' '.join(current) + '.')
            
            return ' '.join(sentences)

@app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>YouTube Transcription</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    max-width: 600px;
                    width: 100%;
                }
                h1 {
                    color: #333;
                    margin-bottom: 30px;
                    font-size: 32px;
                    text-align: center;
                }
                form {
                    display: flex;
                    flex-direction: column;
                    gap: 20px;
                }
                input {
                    padding: 15px;
                    border: 2px solid #e0e0e0;
                    border-radius: 10px;
                    font-size: 16px;
                    transition: border 0.3s;
                }
                input:focus {
                    outline: none;
                    border-color: #667eea;
                }
                button {
                    padding: 15px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: transform 0.2s;
                }
                button:hover {
                    transform: translateY(-2px);
                }
                button:active {
                    transform: translateY(0);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎥 YouTube Transcription</h1>
                <form action="/transcribe" method="post">
                    <input type="text" name="url" placeholder="Paste YouTube URL here..." required>
                    <button type="submit">Get Transcript</button>
                </form>
            </div>
        </body>
        </html>
    ''')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    url = request.form.get('url')
    
    try:
        text = get_transcript(url)
        return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Transcript Result</title>
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        padding: 40px 20px;
                    }
                    .container {
                        background: white;
                        padding: 40px;
                        border-radius: 20px;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                        max-width: 900px;
                        margin: 0 auto;
                    }
                    h1 {
                        color: #333;
                        margin-bottom: 20px;
                        font-size: 28px;
                    }
                    .back-btn {
                        display: inline-block;
                        padding: 10px 20px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        text-decoration: none;
                        border-radius: 8px;
                        margin-bottom: 30px;
                        font-weight: 600;
                        transition: transform 0.2s;
                    }
                    .back-btn:hover {
                        transform: translateY(-2px);
                    }
                    .transcript {
                        background: #f8f9fa;
                        padding: 30px;
                        border-radius: 12px;
                        line-height: 1.8;
                        color: #333;
                        font-size: 16px;
                        text-align: justify;
                    }
                    .copy-btn {
                        margin-top: 20px;
                        padding: 12px 24px;
                        background: #28a745;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        cursor: pointer;
                        font-weight: 600;
                        transition: background 0.3s;
                    }
                    .copy-btn:hover {
                        background: #218838;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📝 Transcript</h1>
                    <a href="/" class="back-btn">← Back</a>
                    <div class="transcript" id="transcript">{{ text }}</div>
                    <button class="copy-btn" onclick="copyText()">Copy to Clipboard</button>
                </div>
                <script>
                    function copyText() {
                        const text = document.getElementById('transcript').innerText;
                        navigator.clipboard.writeText(text).then(() => {
                            const btn = document.querySelector('.copy-btn');
                            btn.textContent = '✓ Copied!';
                            setTimeout(() => btn.textContent = 'Copy to Clipboard', 2000);
                        });
                    }
                </script>
            </body>
            </html>
        ''', text=text)
    except Exception as e:
        return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Error</title>
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        padding: 20px;
                    }
                    .container {
                        background: white;
                        padding: 40px;
                        border-radius: 20px;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                        max-width: 600px;
                        text-align: center;
                    }
                    h1 {
                        color: #dc3545;
                        margin-bottom: 20px;
                        font-size: 28px;
                    }
                    p {
                        color: #666;
                        margin-bottom: 15px;
                        line-height: 1.6;
                    }
                    .back-btn {
                        display: inline-block;
                        margin-top: 20px;
                        padding: 12px 24px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        text-decoration: none;
                        border-radius: 8px;
                        font-weight: 600;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>❌ Error</h1>
                    <p>Could not get transcript. This video may not have captions available.</p>
                    <p style="font-size: 14px; color: #999;">{{ error }}</p>
                    <a href="/" class="back-btn">← Try Another Video</a>
                </div>
            </body>
            </html>
        ''', error=str(e)), 500

@app.route('/api/transcribe', methods=['POST'])
def api_transcribe():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    try:
        text = get_transcript(url)
        return jsonify({'transcript': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
