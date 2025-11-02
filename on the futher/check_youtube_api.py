import youtube_transcript_api
import sys, inspect

print("✅ Python exe:", sys.executable)
print("✅ youtube_transcript_api loaded from:", getattr(youtube_transcript_api, "__file__", "❌ no __file__"))
print("✅ dir(youtube_transcript_api):", list(dir(youtube_transcript_api))[:50])

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    print("✅ Successfully imported YouTubeTranscriptApi")
    print("✅ Attributes of class:", [x for x in dir(YouTubeTranscriptApi) if not x.startswith('_')])
except Exception as e:
    print("❌ Import failed:", e)

print("\n==== Checking transcript fetch ====")
try:
    api = youtube_transcript_api.YouTubeTranscriptApi
    print("🧩 Type of api:", api)
    if hasattr(api, "get_transcript"):
        print("✅ get_transcript exists!")
    else:
        print("❌ get_transcript NOT found!")
except Exception as e:
    print("⚠️ Error while checking:", e)
