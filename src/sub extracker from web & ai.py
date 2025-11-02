# -*- coding: utf-8 -*-
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from deep_translator import GoogleTranslator
from tqdm import tqdm
import time
import sys
import yt_dlp
import re
from pathlib import Path


# ===== 1. تنظیم آیدی ویدیو =====
video_id = "hSTy_BInQs8"  # فقط آیدی ویدیو رو اینجا بذار
video_url = f"https://www.youtube.com/watch?v={video_id}"


# ===== 2. تابع برای گرفتن عنوان ویدیو =====
def get_video_title(url):
    try:
        ydl_opts = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "untitled_video")
            # حذف کاراکترهای غیرمجاز برای نام فایل
            title = re.sub(r'[\\/*?:"<>|]', "_", title)
            return title
    except Exception as e:
        print(f"⚠️ خطا در دریافت عنوان ویدیو: {e}")
        return "untitled_video"


# ===== 3. گرفتن عنوان =====
video_title = get_video_title(video_url)
Path("files").mkdir(exist_ok=True)
output_file = Path("files") / f"{video_title}.srt"


# ===== 4. تابع تبدیل زمان به فرمت SRT =====
def srt_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int((sec - int(sec)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


# ===== 5. دریافت زیرنویس =====
try:
    print("⏳ در حال دریافت لیست زیرنویس‌ها از یوتیوب...")
    api = YouTubeTranscriptApi()
    transcript_list = api.list(video_id)
    transcript = transcript_list.find_transcript(['en'])
    data = transcript.fetch()
except (TranscriptsDisabled, NoTranscriptFound):
    print("❌ این ویدیو زیرنویس انگلیسی ندارد یا غیرفعال است.")
    sys.exit()
except Exception as e:
    print("⚠️ خطا در دریافت زیرنویس:", e)
    sys.exit()


# ===== 6. ترجمه و ساخت فایل =====
translator = GoogleTranslator(source='en', target='fa')

print(f"🌍 در حال ترجمه و ساخت زیرنویس برای «{video_title}»...\n")

with open(output_file, "w", encoding="utf-8") as f:
    for i, entry in enumerate(tqdm(data, desc="🔄 ترجمه و ساخت فایل", unit="خط"), 1):
        start = entry.start
        duration = entry.duration
        end = start + duration
        text_en = entry.text.replace('\n', ' ')
        try:
            text_fa = translator.translate(text_en)
        except Exception:
            text_fa = "❌ ترجمه انجام نشد"

        f.write(f"{i}\n{srt_time(start)} --> {srt_time(end)}\n{text_en}\n{text_fa}\n\n")
        time.sleep(0.3)  # جلوگیری از بلاک‌شدن توسط Google Translate

print(f"\n✅ زیرنویس دو زبانه ساخته شد: {output_file.name}")
