from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import openai
import os
import cv2
from src.search import get_full_transcript, find_best_video_segment, load_config
from fastapi.responses import StreamingResponse
from fastapi.responses import FileResponse

# Load API Key
config = load_config()
api_key = config.get("openai_api_key", None)

if not api_key or not api_key.startswith("sk-"):
    raise ValueError("❌ ERROR: OpenAI API key is missing or incorrect. Check config.yaml!")

# Initialize FastAPI app
app = FastAPI()

VIDEO_PATH = "data/videos/march_11.mp4"

# Serve static files (like videos)
app.mount("/static", StaticFiles(directory="data/videos"), name="static")

# Allow frontend to connect to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to frontend URL for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_video_duration(video_path):
    """Fetches the duration of a video in seconds."""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("❌ ERROR: Could not open video file.")
            return None
        fps = cap.get(cv2.CAP_PROP_FPS)  
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  
        duration = frame_count / fps  
        cap.release()
        return int(duration)  
    except Exception as e:
        print(f"❌ ERROR getting video duration: {e}")
        return None

@app.get("/")
def home():
    return {"message": "Welcome to the Immigration Law Chatbot API"}

@app.get("/ask")
def ask_question(query: str):
    """Handles chatbot questions and returns the video timestamp."""
    print(f"🔍 Received query: {query}")  

    full_transcript_text, structured_transcript = get_full_transcript()
    print("📜 Loaded full transcript.")  

    video_duration = get_video_duration(VIDEO_PATH)
    if video_duration is None:
        return {"error": "Could not fetch video duration."}

    # Step 1: Generate AI response
    chat_prompt = f"""
    You are a legal chatbot specializing in U.S. immigration law.
    Use your knowledge + the podcast transcript to answer user queries.

    **User Question:** {query}

    **Podcast Transcript:** (Full text provided)
    {full_transcript_text}

    Answer in **under 300 words**. Be **direct** but informative.
    """

    print("🤖 Sending request to OpenAI for response...")  

    client = openai.OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a concise, expert immigration chatbot."},
                {"role": "user", "content": chat_prompt}
            ]
        )
        chat_response = response.choices[0].message.content.strip()
        print("✅ AI Response received.")  
    except Exception as e:
        print(f"❌ ERROR generating AI response: {e}")
        chat_response = f"Error generating AI response: {e}"

    # Step 2: Find the best timestamp for the response
    best_timestamp = find_best_video_segment(query, chat_response, full_transcript_text, structured_transcript, video_duration)

    # Generate the formatted video response
    if best_timestamp is not None:
        video_response = f"""
        {chat_response}

        🔹 **Watch the relevant section of the podcast here:**  
        <video width="600" controls>
            <source src="/video" type="video/mp4">
            Your browser does not support the video tag.
        </video>

        ⏩ **Seek to timestamp:** {best_timestamp} seconds.
        """
    else:
        video_response = f"{chat_response}\n\n❌ No relevant timestamp found in the transcript."

    return {
        "response": video_response,
        "timestamp": best_timestamp,
    }

def generate_video_stream(file_path, start_time=0):
    """Streams video from a given timestamp"""
    with open(file_path, "rb") as video_file:
        video_file.seek(start_time)  # FastAPI does not natively seek, but we return the full file
        yield from video_file

@app.get("/video")
def get_video():
    """Serves the full video file for embedding in the UI."""
    if not os.path.exists(VIDEO_PATH):
        return {"error": "Video file not found"}

    return FileResponse(VIDEO_PATH, media_type="video/mp4")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)