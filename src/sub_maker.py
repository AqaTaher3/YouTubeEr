import re
from pathlib import Path

# ---------- تبدیل زمان‌های مختلف به ثانیه ----------
def parse_time_to_seconds(t: str) -> float:
    """
    پشتیبانی از فرمت‌ها:
      - 12.5   (ثانیه)
      - 12s    (ثانیه)
      - 1:04   (mm:ss)  -> 64
      - 01:02:30 (hh:mm:ss)
    """
    t = t.strip()
    # hh:mm:ss
    m = re.match(r"^(\d+):(\d{2}):(\d{2})(?:\.\d+)?$", t)
    if m:
        h, mm, ss = map(int, m.groups())
        return h*3600 + mm*60 + ss
    # mm:ss
    m = re.match(r"^(\d+):(\d{2})(?:\.\d+)?$", t)
    if m:
        mm, ss = map(int, m.groups())
        return mm*60 + ss
    # decimal seconds or with s
    m = re.match(r"^(\d+(?:\.\d+)?)(?:s)?$", t)
    if m:
        return float(m.group(1))
    raise ValueError(f"Unknown time format: {t}")

# ---------- تبدیل ثانیه به فرمت SRT ----------
def seconds_to_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds * 1000) % 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

# ---------- پارسر مقاوم ----------
def parse_flexible(input_text: str):
    """
    الگوریتم:
      - هر خطی که با زمان شروع شود (مثلاً '0s' یا '1:04' یا '12') شروع یک بلوک جدید است.
      - اگر بعد از زمان، محتوا در همان خط باشد آن را شروع بلوک در نظر می‌گیریم، در غیر این صورت
        خطوط بعدی تا خطی که با زمان شروع می‌شود جزو محتوای همان بلوک هستند.
      - برای جدا کردن انگلیسی/فارسی ترجیه می‌دهیم:
          1) اگر تب (\t) بود جدا کنیم
          2) در غیر اینصورت محل اولین کاراکتر فارسی را پیدا کنیم و آنجا جدا کنیم
          3) اگر باز هم نبود، تلاش می‌کنیم با دو فاصله یا ' | ' جدا کنیم
    """
    lines = input_text.splitlines()
    # الگوی تشخیص زمان در ابتدای خط (قابل قبول: 1:04  or 12s or 12.5 or 123)
    time_at_start = re.compile(r"^\s*(\d+(?::\d{2}){0,2}(?:\.\d+)?(?:s)?)\b")
    entries = []  # list of (start_seconds, content_string)
    cur_time = None
    cur_parts = []

    for ln in lines:
        s = ln.rstrip("\n")
        m = time_at_start.match(s)
        if m:
            # زمان جدید؛ ذخیره رکورد قبلی اگر بود
            if cur_time is not None:
                content = "\n".join(cur_parts).strip()
                entries.append((cur_time, content))
            # مقدار زمان جدید
            time_str = m.group(1)
            try:
                cur_time = parse_time_to_seconds(time_str)
            except ValueError:
                # اگر به هر دلیلی زمان قابل parse نبود، از ادامه خط صرف‌نظر می‌کنیم
                cur_time = None
                cur_parts = []
                continue
            # بقیهٔ خط بعد از زمان
            rest = s[m.end():].lstrip(" \t")
            cur_parts = [rest] if rest != "" else []
        else:
            # ادامه محتوا برای رکورد جاری (اگر رکوردی باز باشه)
            if cur_time is not None:
                cur_parts.append(s)
            else:
                # خطی که نه زمان داره و نه درون رکورد—نادیده گرفته می‌شود
                continue

    # ذخیره آخرین رکورد
    if cur_time is not None:
        content = "\n".join(cur_parts).strip()
        entries.append((cur_time, content))

    # حالا هر entry را به en/fa جدا می‌کنیم
    persian_re = re.compile(r"[\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]")
    subs = []
    for t, content in entries:
        en = ""
        fa = ""
        if not content:
            en = ""
            fa = ""
        else:
            if "\t" in content:
                parts = content.split("\t")
                en = "\t".join(parts[:-1]).strip() if len(parts) > 1 else parts[0].strip()
                fa = parts[-1].strip() if len(parts) > 1 else ""
            else:
                # جستجوی اولین حرف فارسی
                mfa = persian_re.search(content)
                if mfa:
                    idx = mfa.start()
                    en = content[:idx].strip()
                    fa = content[idx:].strip()
                else:
                    # اگر فارسی وجود نداشت، سعی کنیم با دو فاصله یا ' | ' جدا کنیم
                    if "  " in content:
                        parts = re.split(r"\s{2,}", content, maxsplit=1)
                        en = parts[0].strip()
                        fa = parts[1].strip() if len(parts) > 1 else ""
                    elif " | " in content:
                        parts = content.split(" | ", 1)
                        en = parts[0].strip()
                        fa = parts[1].strip()
                    else:
                        # fallback: همه محتوا را انگلیسی می‌گذاریم
                        en = content.strip()
                        fa = ""
        subs.append((t, en, fa))
    return subs

# ---------- تولید SRT ----------
def make_srt(subs, default_duration=4.0):
    blocks = []
    for i, (start, en, fa) in enumerate(subs):
        end = subs[i+1][0] if i+1 < len(subs) else start + default_duration
        blocks.append(
            f"{i+1}\n"
            f"{seconds_to_srt_time(start)} --> {seconds_to_srt_time(end)}\n"
            f"{en}\n{fa}\n"
        )
    return "\n".join(blocks) + "\n"

# ---------- تبدیل فایل ----------
def convert_file(input_path: str, output_path: str = None):
    p = Path(input_path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {input_path}")
    text = p.read_text(encoding="utf-8", errors="ignore")
    subs = parse_flexible(text)
    print(f"ورودی: {len(text.splitlines())} خط — خروجی: {len(subs)} آیتم زیرنویس.")
    # نمونه‌های اولیه برای دیباگ
    for i, it in enumerate(subs[:5], start=1):
        t, en, fa = it
        print(f"نمونه {i}: time={t} en_len={len(en)} fa_len={len(fa)}")
    srt_text = make_srt(subs)
    if output_path is None:
        output_path = str(p.with_suffix(".srt"))
    Path(output_path).write_text(srt_text, encoding="utf-8")
    print(f"✅ ساخته شد: {output_path}")

# ---------- مثال اجرا ----------
if __name__ == "__main__":
    # مسیر فایل ورودی رو اینجا بگذار
    input_path = r"A:\00_projects\you_tube\files\obisidian.txt"
    convert_file(input_path)
