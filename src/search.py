import openai
import json
import pinecone
import yaml
import os
import pinecone

# Load API keys from config.yaml
def load_config():
    with open("config/config.yaml", "r") as file:
        return yaml.safe_load(file)

config = load_config()
openai.api_key = config["openai_api_key"]

# Initialize Pinecone (Vector Database)
pinecone.init(api_key=config["pinecone_api_key"], environment="us-west1-gcp")

# Create a Pinecone index if it doesn’t exist
if "transcripts" not in pinecone.list_indexes():
    pinecone.create_index("transcripts", dimension=1536)

index = pinecone.Index("transcripts")

def store_transcript(transcript_path):
    """Converts transcript text into AI embeddings and stores them."""
    with open(transcript_path, "r") as f:
        transcript_data = json.load(f)

    for segment in transcript_data:
        text = segment["text"]
        embedding = openai.Embedding.create(input=text, model="text-embedding-ada-002")["data"][0]["embedding"]
        index.upsert([(str(segment["start_time"]), embedding, {"text": text})])

    print(f"✅ Stored transcript: {transcript_path}")

if __name__ == "__main__":
    transcript_json_file = "data/structured_transcripts/march_11.json"  # Change to actual filename
    if os.path.exists(transcript_json_file):
        store_transcript(transcript_json_file)
    else:
        print(f"❌ ERROR: Transcript file not found at {transcript_json_file}!")