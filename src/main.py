# -*- coding: utf-8 -*-
from pathlib import Path
import yt_dlp
from sub_extracker import get_video_title, srt_time
from youtube_transcript_api import YouTubeTranscriptApi
from deep_translator import GoogleTranslator
from tqdm import tqdm
import re
import time


def download_single_video(url: str):
    """دانلود یک ویدیو با yt-dlp و بازگشت آیدی و عنوان"""
    Path("files").mkdir(exist_ok=True)

    ydl_opts = {
        "quiet": True,
        "skip_download": False,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en"],
        "subtitlesformat": "srt",
        "outtmpl": "files/%(title)s.%(ext)s",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = re.sub(r'[\\/*?:"<>|]', "_", info.get("title", "video"))
        video_id = info.get("id")
        print(f"✅ ویدیو '{title}' با موفقیت دانلود شد.")
        return video_id, title


def make_separate_subs(video_id: str, video_title: str):
    """ساخت زیرنویس‌های جداگانه فارسی و انگلیسی"""
    try:
        print("⏳ در حال دریافت زیرنویس از یوتیوب...")
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en'])
        data = transcript.fetch()
    except Exception as e:
        print(f"❌ خطا در دریافت زیرنویس: {e}")
        return

    # مسیر فایل‌ها
    file_en = Path("files") / f"{video_title}.en.srt"
    file_fa = Path("files") / f"{video_title}.fa.srt"

    translator = GoogleTranslator(source="en", target="fa")

    with open(file_en, "w", encoding="utf-8") as f_en, open(file_fa, "w", encoding="utf-8") as f_fa:
        for i, entry in enumerate(tqdm(data, desc="📝 ساخت زیرنویس‌ها", unit="خط"), 1):
            start = entry['start']
            end = start + entry['duration']
            text_en = entry['text'].replace("\n", " ")

            try:
                text_fa = translator.translate(text_en)
            except Exception:
                text_fa = "❌ ترجمه انجام نشد"

            f_en.write(f"{i}\n{srt_time(start)} --> {srt_time(end)}\n{text_en}\n\n")
            f_fa.write(f"{i}\n{srt_time(start)} --> {srt_time(end)}\n{text_fa}\n\n")
            time.sleep(0.3)

    print(f"\n✅ زیرنویس انگلیسی: {file_en.name}")
    print(f"✅ زیرنویس فارسی: {file_fa.name}")


if __name__ == "__main__":
    # url = input("🔗 لینک یوتیوب ویدیو را وارد کنید: ").strip()
    url = "https://www.youtube.com/watch?v=z4AbijUCoKU&t=4s"
    # ۱. دانلود ویدیو
    video_id, video_title = download_single_video(url)

    # ۲. ساخت زیرنویس‌ها (فارسی و انگلیسی جدا)
    make_separate_subs(video_id, video_title)

    print("\n🎉 عملیات با موفقیت انجام شد.")