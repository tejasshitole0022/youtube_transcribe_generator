# YouTube Video Transcription

Extract spoken text from YouTube videos.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

### Flask Web App

```bash
python app.py
```

Open http://localhost:5000 in your browser, paste a YouTube URL, and get the transcript.

### API Endpoint

```bash
curl -X POST http://localhost:5000/api/transcribe \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

### Command Line

```bash
python transcribe.py <youtube_url>
```

## Note

Only works with videos that have captions/subtitles available.
