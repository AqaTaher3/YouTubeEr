# -*- coding: utf-8 -*-
import json
import subprocess
from pathlib import Path
from tqdm import tqdm  # ✅ برای نوار پیشرفت


def download_videos(config_path: str):
    """دانلود ویدیوها طبق فایل تنظیمات"""
    # فایل JSON را بخوان
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    download_path = Path(config["download_path"])
    download_path.mkdir(parents=True, exist_ok=True)

    videos = config["videos"]

    print(f"🎬 تعداد ویدیوهای موجود در لیست: {len(videos)}\n")

    # tqdm برای نوار پیشرفت دانلودها
    for vid in tqdm(videos, desc="⬇️ دانلود ویدیوها", unit="ویدیو"):
        if not vid.get("enabled", True):
            tqdm.write(f"⏸ ویدیو '{vid['title']}' غیرفعال است — رد شد.")
            continue

        tqdm.write(f"▶️ در حال دانلود: {vid['title']}")

        cmd = [
            "yt-dlp",
            "-f", vid["download_format"],
            "-o", str(download_path / f"{vid['id']}.%(ext)s"),
            vid["url"]
        ]

        # اگر زیرنویس فعال بود
        subs = vid.get("subtitles", {})
        if subs.get("enabled"):
            cmd += [
                "--write-auto-subs",
                "--sub-langs", ",".join(subs.get("languages", [])),
                "--convert-subs", "srt"
            ]

        # اجرای yt-dlp با کنترل خطا
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            tqdm.write(f"✅ دانلود '{vid['title']}' انجام شد.")
        except subprocess.CalledProcessError as e:
            tqdm.write(f"❌ خطا در دانلود '{vid['title']}': {e}")

    print("\n🎉 همه‌ی دانلودهای فعال انجام شدند.")


if __name__ == "__main__":
    download_videos("files/to_download.json")

# ffmpeg -i "video.webm" -c copy "video.mp4"
# ffmpeg -i "aaa.webm" -vf subtitles="bbb.srt" "aaa_sub.mp4"
