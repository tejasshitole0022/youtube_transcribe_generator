import sys
import yt_dlp
import json

def get_transcript(url):
    """Get transcript from YouTube video"""
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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <youtube_url>")
        sys.exit(1)
    
    url = sys.argv[1]
    text = get_transcript(url)
    
    if text:
        print("\n--- TRANSCRIPT ---\n")
        print(text)
        
        # Save to file
        with open('transcript.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        print("\n\nSaved to transcript.txt")
