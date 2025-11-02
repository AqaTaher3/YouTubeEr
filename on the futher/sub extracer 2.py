# -*- coding: utf-8 -*-
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from deep_translator import GoogleTranslator
from tqdm import tqdm
import time
import sys
import yt_dlp
import re
from pathlib import Path


# ===== تنظیمات =====
video_id = "dQw4w9WgXcQ"  # فقط آیدی ویدیو
video_url = f"https://www.youtube.com/watch?v={video_id}"
BATCH_SIZE = 8  # 👈 تعداد خطوطی که با هم ترجمه می‌شن (بهتره 5 تا 10 باشه)


# ===== گرفتن عنوان ویدیو از یوتیوب =====
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


video_title = get_video_title(video_url)
output_file = Path(f"{video_title}.srt")


# ===== تابع تبدیل زمان =====
def srt_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int((sec - int(sec)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


# ===== دریافت زیرنویس =====
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


# ===== ترجمه‌ی دسته‌ای و ساخت فایل =====
translator = GoogleTranslator(source='en', target='fa')
print(f"🌍 در حال ترجمه و ساخت زیرنویس برای «{video_title}»...\n")

with open(output_file, "w", encoding="utf-8") as f:
    for i in tqdm(range(0, len(data), BATCH_SIZE), desc="🔄 ترجمه دسته‌ای", unit="بچ"):
        batch = data[i:i + BATCH_SIZE]

        # ادغام خطوط انگلیسی
        joined_texts = [entry.text.replace("\n", " ") for entry in batch]
        combined_text = " ||| ".join(joined_texts)

        # ترجمه‌ی کل دسته
        try:
            translated_batch = translator.translate(combined_text)
        except Exception:
            translated_batch = "❌ ترجمه انجام نشد"
            time.sleep(1)
            continue

        # تقسیم ترجمه‌ی خروجی به خطوط جداگانه
        translated_segments = translated_batch.split("|||")

        # ذخیره در فایل
        for j, entry in enumerate(batch):
            idx = i + j + 1
            start = entry.start
            end = start + entry.duration
            text_en = entry.text.replace("\n", " ")
            text_fa = translated_segments[j].strip() if j < len(translated_segments) else "❌"

            f.write(f"{idx}\n{srt_time(start)} --> {srt_time(end)}\n{text_en}\n{text_fa}\n\n")

        # فاصله‌ی کوتاه بین دسته‌ها برای جلوگیری از بلاک شدن
        time.sleep(0.2)

print(f"\n✅ زیرنویس دو زبانه ساخته شد: {output_file.name}")
