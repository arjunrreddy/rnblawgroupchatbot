import os
import json
import re

def txt_to_json(txt_path):
    """Converts a Whisper .txt transcript into a structured JSON file with timestamps."""
    json_output_path = txt_path.replace(".txt", ".json").replace("transcripts", "structured_transcripts")
    os.makedirs(os.path.dirname(json_output_path), exist_ok=True)

    transcript_data = []

    with open(txt_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        match = re.match(r"\[(\d+\.\d+)s\] (.+)", line.strip())
        if match:
            start_time = round(float(match.group(1)), 2)
            text = match.group(2)
            transcript_data.append({
                "start_time": start_time,
                "text": text
            })

    with open(json_output_path, "w") as json_file:
        json.dump(transcript_data, json_file, indent=4)

    print(f"✅ Converted {txt_path} → {json_output_path}")

if __name__ == "__main__":
    transcript_txt_file = "data/transcripts/march_11.txt"  # Change to your actual file
    if os.path.exists(transcript_txt_file):
        txt_to_json(transcript_txt_file)
    else:
        print("❌ ERROR: Transcript file not found!")
