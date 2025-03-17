import whisper
import os

def transcribe_video(video_path):
    """Transcribes a video with Whisper and prints progress in real-time."""
    model = whisper.load_model("small")  # Change to "medium" if needed
    result = model.transcribe(video_path, verbose=True)  # Verbose shows progress

    transcript_path = video_path.replace(".mp4", ".txt").replace("videos", "transcripts")
    os.makedirs(os.path.dirname(transcript_path), exist_ok=True)

    with open(transcript_path, "w") as f:
        for segment in result["segments"]:
            start_time = round(segment["start"], 2)
            text = segment["text"]
            print(f"[{start_time}s] {text}")  # Print transcription in real-time
            f.write(f"[{start_time}s] {text}\n")  # Save to file as it transcribes

    return result["segments"]

if __name__ == "__main__":
    video_file = "data/videos/march_11.mp4"  # Change to actual filename
    if os.path.exists(video_file):
        print(f"🔄 Transcribing: {video_file} ...")
        segments = transcribe_video(video_file)
        print("✅ Transcription Complete! Check `data/transcripts/`")
    else:
        print("❌ ERROR: Video file not found! Make sure it's in `data/videos/`")

