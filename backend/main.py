from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import openai
import yaml
from search import search_transcript, get_most_relevant_timestamp  # Ensure these exist

# Initialize FastAPI app
app = FastAPI()

# Allow frontend to connect to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific frontend URL if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Welcome to the Immigration Law Chatbot API"}

@app.get("/ask")
def ask_question(query: str):
    """Handles chatbot questions"""
    
    # Ensure transcript search function exists
    search_results = search_transcript(query, top_k=5)
    
    if not search_results:
        return {
            "response": "I couldn't find relevant information in the podcast transcript.",
            "references": "No relevant video sections found."
        }

    # Extract full transcript text for ChatGPT
    full_transcript_text = "\n".join([
        f"({result['timestamp']}s) {result['answer']}" for result in search_results
    ])

    # Find the most relevant timestamp
    best_timestamp, best_video_link = get_most_relevant_timestamp(search_results)

    # Format the best video link
    best_video_link = f"{best_video_link}&t={best_timestamp}s" if best_video_link else "No video available"

    # Generate OpenAI response
    chat_prompt = f"""
    You are a legal chatbot assistant specializing in immigration law. 
    Use the following transcript snippets to answer user queries:

    User Question: {query}
    
    Podcast Transcript:
    {full_transcript_text}
    
    Provide an answer referencing relevant timestamps.
    """

    client = openai.OpenAI(api_key="YOUR_OPENAI_API_KEY")  # Load API key correctly

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a legal chatbot."},
                {"role": "user", "content": chat_prompt}
            ]
        )
        chat_response = response.choices[0].message.content
    except Exception as e:
        chat_response = f"Error generating AI response: {e}"

    return {
        "response": chat_response,
        "references": best_video_link
    }
