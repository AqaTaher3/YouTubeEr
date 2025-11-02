from youtube_transcript_api import YouTubeTranscriptApi
from deep_translator import GoogleTranslator

# ===== 1. لینک یوتیوب =====
video_id = "dQw4w9WgXcQ"  # فقط آیدی ویدیو رو بزار اینجا

# ===== 2. دریافت زیرنویس انگلیسی =====
transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])

# ===== 3. ترجمه و ساخت فایل =====
translator = GoogleTranslator(source='en', target='fa')

with open("subtitle_bilingual.srt", "w", encoding="utf-8") as f:
    for i, entry in enumerate(transcript, 1):
        start = entry['start']
        duration = entry['duration']
        end = start + duration
        text_en = entry['text'].replace('\n', ' ')
        text_fa = translator.translate(text_en)


        # زمان را به قالب SRT تبدیل می‌کنیم
        def srt_time(sec):
            h = int(sec // 3600)
            m = int((sec % 3600) // 60)
            s = int(sec % 60)
            ms = int((sec - int(sec)) * 1000)
            return f"{h:02}:{m:02}:{s:02},{ms:03}"


        f.write(f"{i}\n{srt_time(start)} --> {srt_time(end)}\n{text_en}\n{text_fa}\n\n")

print("✅ زیرنویس دو زبانه ساخته شد: subtitle_bilingual.srt")

# https://www.youtube.com/watch?v=z4AbijUCoKU
# https://www.youtube.com/watch?v=UQN63sucxA4
# https://www.youtube.com/watch?v=6iiqR4UGZqM
# https://www.youtube.com/watch?v=1XMBQN9WFyg
#  first sub
# https://www.youtube.com/watch?v=hSTy_BInQs8&t=332s