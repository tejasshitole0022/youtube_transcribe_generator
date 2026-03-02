from flask import Flask, request, jsonify, render_template_string
import yt_dlp
import json
from deep_translator import GoogleTranslator

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
            <title>YouTube Transcription1</title>
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
                        max-width: 1200px;
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
                    .transcript-container {
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 20px;
                    }
                    .transcript-box {
                        background: #f8f9fa;
                        padding: 30px;
                        border-radius: 12px;
                        line-height: 1.8;
                        color: #333;
                        font-size: 16px;
                    }
                    .transcript-box h3 {
                        margin-bottom: 15px;
                        color: #667eea;
                    }
                    .sentence {
                        cursor: pointer;
                        padding: 4px 0;
                        transition: all 0.2s;
                        border-radius: 4px;
                    }
                    .sentence:hover {
                        background: #e3f2fd;
                    }
                    .sentence.highlight {
                        background: #bbdefb;
                        font-weight: 500;
                    }
                    .marathi-text {
                        font-size: 18px;
                    }
                    .loading {
                        text-align: center;
                        color: #999;
                        font-style: italic;
                    }
                    .actions {
                        margin-top: 20px;
                        display: flex;
                        gap: 10px;
                    }
                    .copy-btn {
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
                    .translate-btn {
                        padding: 12px 24px;
                        background: #ff6b6b;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        cursor: pointer;
                        font-weight: 600;
                        transition: background 0.3s;
                    }
                    .translate-btn:hover {
                        background: #ee5a52;
                    }
                    @media (max-width: 768px) {
                        .transcript-container {
                            grid-template-columns: 1fr;
                        }
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📝 Transcript</h1>
                    <a href="/" class="back-btn">← Back</a>
                    
                    <div class="transcript-container">
                        <div class="transcript-box">
                            <h3>🇬🇧 English</h3>
                            <div id="english">{{ text }}</div>
                        </div>
                        <div class="transcript-box">
                            <h3>🇮🇳 मराठी (Marathi)</h3>
                            <div id="marathi" class="marathi-text loading">Click "Translate to Marathi" button below</div>
                        </div>
                    </div>
                    
                    <div class="actions">
                        <button class="translate-btn" onclick="translateText()">Translate to Marathi</button>
                        <button class="copy-btn" onclick="copyText('english')">Copy English</button>
                        <button class="copy-btn" onclick="copyText('marathi')">Copy Marathi</button>
                    </div>
                </div>
                <script>
                    async function translateText() {
                        const btn = document.querySelector('.translate-btn');
                        const marathiDiv = document.getElementById('marathi');
                        const englishText = document.getElementById('english').innerText;
                        
                        btn.disabled = true;
                        btn.textContent = 'Translating...';
                        marathiDiv.innerHTML = '<div class="loading">Translating...</div>';
                        
                        try {
                            const response = await fetch('/translate', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({text: englishText})
                            });
                            
                            if (!response.ok) {
                                throw new Error('Translation failed');
                            }
                            
                            const data = await response.json();
                            
                            if (data.error) {
                                throw new Error(data.error);
                            }
                            
                            const englishDiv = document.getElementById('english');
                            englishDiv.innerHTML = '';
                            marathiDiv.innerHTML = '';
                            marathiDiv.classList.remove('loading');
                            
                            data.english_sentences.forEach((sent, i) => {
                                const engSpan = document.createElement('span');
                                engSpan.className = 'sentence';
                                engSpan.textContent = sent + ' ';
                                engSpan.dataset.index = i;
                                engSpan.onmouseenter = () => highlightPair(i);
                                engSpan.onmouseleave = () => clearHighlight();
                                englishDiv.appendChild(engSpan);
                                
                                const marSpan = document.createElement('span');
                                marSpan.className = 'sentence';
                                marSpan.textContent = data.marathi_sentences[i] + ' ';
                                marSpan.dataset.index = i;
                                marSpan.onmouseenter = () => highlightPair(i);
                                marSpan.onmouseleave = () => clearHighlight();
                                marathiDiv.appendChild(marSpan);
                            });
                            
                            btn.textContent = '✓ Translated';
                        } catch (error) {
                            console.error('Translation error:', error);
                            marathiDiv.innerHTML = '<div class="loading">Translation failed: ' + error.message + '</div>';
                            btn.disabled = false;
                            btn.textContent = 'Translate to Marathi';
                        }
                    }
                    
                    function highlightPair(index) {
                        document.querySelectorAll('.sentence').forEach(el => {
                            if (el.dataset.index == index) {
                                el.classList.add('highlight');
                            }
                        });
                    }
                    
                    function clearHighlight() {
                        document.querySelectorAll('.sentence').forEach(el => {
                            el.classList.remove('highlight');
                        });
                    }
                    
                    function copyText(lang) {
                        const text = document.getElementById(lang).innerText;
                        navigator.clipboard.writeText(text).then(() => {
                            const btn = event.target;
                            const original = btn.textContent;
                            btn.textContent = '✓ Copied!';
                            setTimeout(() => btn.textContent = original, 2000);
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

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        translator = GoogleTranslator(source='en', target='mr')
        translated_sentences = [translator.translate(s) for s in sentences]
        
        return jsonify({
            'english_sentences': sentences,
            'marathi_sentences': translated_sentences
        })
    except Exception as e:
        print(f"Translation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Translation failed: {str(e)}'}), 500

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
