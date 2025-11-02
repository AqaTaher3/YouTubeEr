import json
import subprocess
from pathlib import Path


def download_videos(config_path: str):
    # فایل JSON را بخوان
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    download_path = Path(config["download_path"])
    download_path.mkdir(parents=True, exist_ok=True)

    for vid in config["videos"]:
        if not vid.get("enabled", True):
            print(f"⏸ ویدیو '{vid['title']}' غیرفعال است — رد شد.")
            continue

        print(f"⬇️ در حال دانلود: {vid['title']}")

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

        subprocess.run(cmd, check=True)

    print("✅ همه دانلودهای فعال انجام شد.")


if __name__ == "__main__":
    download_videos("files/to_download.json")

# ffmpeg -i "video.webm" -c copy "video.mp4"
#  ffmpeg -i "aaa.webm" -vf subtitles="bbb.srt" "aaa_sub.mp4"*