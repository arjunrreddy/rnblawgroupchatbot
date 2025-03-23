from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import openai
from src.search import get_full_transcript, find_best_video_segment, load_config

# Load API Key
config = load_config()
api_key = config.get("openai_api_key", None)

if not api_key or not api_key.startswith("sk-"):
    raise ValueError("❌ ERROR: OpenAI API key is missing or incorrect. Check config.yaml!")

# External video URL (Dropbox, S3, etc.)
EXTERNAL_VIDEO_URL = "https://www.dropbox.com/scl/fi/yz7xlp3qo3h95p4r0xtjv/march_11.mp4?rlkey=u9frr2ar77ohfhnenvkqleo0j&st=ldp6pqqo&dl=1"

# Initialize FastAPI app
app = FastAPI()

# Allow frontend to connect to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to specific frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Welcome to the Immigration Law Chatbot API"}

@app.get("/ask")
def ask_question(query: str):
    print(f"🔍 Received query: {query}")  

    # Load transcript
    full_transcript_text, structured_transcript = get_full_transcript()
    print("📜 Loaded full transcript.")  

    # Generate AI response
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
        return {
            "response": f"❌ Error generating AI response: {e}",
            "timestamp": None,
            "video_url": None
        }

    # Find the best timestamp
    best_timestamp = find_best_video_segment(
        query,
        chat_response,
        full_transcript_text,
        structured_transcript,
        video_duration=3600  # 1 hour max for external video fallback
    )

    return {
        "response": chat_response,
        "timestamp": best_timestamp,
        "video_url": EXTERNAL_VIDEO_URL
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)