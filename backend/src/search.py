import yaml
import openai
import json
import faiss
import numpy as np
import os
from openai import OpenAI

# Constants
EMBEDDINGS_FILE = "data/embeddings.json"
INDEX_FILE = "data/faiss_index.idx"
TRANSCRIPT_FILE = "data/structured_transcripts/march_11.json"
VIDEO_URL = "https://www.facebook.com/rnlawgroupUS/videos/498204740023527/"

# Load API Key
def load_config():
    with open("config/config.yaml", "r") as file:
        return yaml.safe_load(file)

config = load_config()
api_key = config.get("openai_api_key", None)

if not api_key or not api_key.startswith("sk-"):
    raise ValueError("❌ ERROR: OpenAI API key is missing or incorrect. Check config.yaml!")

client = OpenAI(api_key=api_key)

def generate_embedding(text):
    """Generate an OpenAI embedding using the updated API format."""
    try:
        response = client.embeddings.create(
            input=[text],  # OpenAI requires input as a list
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ ERROR: Failed to generate embedding: {e}")
        return None  # Return None to avoid script breakage

def store_transcript():
    """Converts transcript text into AI embeddings and stores them locally."""
    if not os.path.exists(TRANSCRIPT_FILE):
        print(f"❌ ERROR: Transcript file not found at {TRANSCRIPT_FILE}!")
        return

    with open(TRANSCRIPT_FILE, "r") as f:
        transcript_data = json.load(f)

    embeddings_data = []
    embeddings_list = []

    print(f"🔍 Found {len(transcript_data)} transcript segments. Generating embeddings...")

    for i, segment in enumerate(transcript_data):
        text = segment["text"]
        timestamp = segment["start_time"]

        print(f"🔹 Processing segment {i+1}/{len(transcript_data)}: {text[:50]}...")  # Show first 50 chars

        embedding = generate_embedding(text)
        if embedding:
            embeddings_data.append({
                "start_time": timestamp,
                "text": text,
                "video_link": VIDEO_URL,
                "embedding": embedding
            })
            embeddings_list.append(embedding)
        else:
            print(f"❌ Skipping segment {i+1} due to embedding error.")

    if not embeddings_list:
        print("❌ ERROR: No valid embeddings were generated. Exiting...")
        return

    # Save embeddings to JSON
    with open(EMBEDDINGS_FILE, "w") as f:
        json.dump(embeddings_data, f, indent=4)

    # Store FAISS index
    dimension = len(embeddings_list[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings_list, dtype=np.float32))
    faiss.write_index(index, INDEX_FILE)

    print(f"✅ Stored embeddings in {EMBEDDINGS_FILE}")
    print(f"✅ FAISS index saved in {INDEX_FILE}")

def search_transcript(query, top_k=3):
    """Finds the most relevant transcript segments for a given question using FAISS."""
    if not os.path.exists(EMBEDDINGS_FILE) or not os.path.exists(INDEX_FILE):
        print("❌ ERROR: No stored embeddings found. Run `store_transcript()` first!")
        return []

    # Load embeddings from file
    with open(EMBEDDINGS_FILE, "r") as f:
        embeddings_data = json.load(f)

    # Load FAISS index
    index = faiss.read_index(INDEX_FILE)

    # Generate embedding for query
    query_embedding = np.array([generate_embedding(query)], dtype=np.float32)

    # Search FAISS index
    distances, indices = index.search(query_embedding, top_k)

    # Debugging logs
    print(f"🎯 FAISS Found Matches: {indices} with distances {distances}")

    results = []
    for idx in indices[0]:
        if idx < len(embeddings_data):
            start_time = max(0, int(embeddings_data[idx]["start_time"]) - 2)  # Show 2 sec earlier for context
            results.append({
                "answer": embeddings_data[idx]["text"],
                "timestamp": start_time,
                "video_link": embeddings_data[idx]["video_link"]
            })

    return results

if __name__ == "__main__":
    print("📌 Storing transcript embeddings...")
    store_transcript()
    print("✅ Embeddings stored successfully!")