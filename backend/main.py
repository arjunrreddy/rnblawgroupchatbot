from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import openai
import sys
import os
from src.search import search_transcript

# Initialize FastAPI app
app = FastAPI()

# Allow frontend to connect to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

    # Search transcript for relevant snippets
    top_snippets = search_transcript(query, top_k=5)

    # ✅ If no results found, return a message
    if not top_snippets:
        return {
            "response": "I couldn't find relevant information in the podcast transcript.",
            "references": "No relevant video sections found."
        }

    # Combine transcript snippets
    full_transcript_text = "\n".join([
        f"({result['timestamp']}s) {result['answer']}" for result in top_snippets
    ])

    # Find best snippet to recommend
    best_snippet = top_snippets[0]  # Use the most relevant snippet
    best_timestamp = best_snippet["timestamp"]
    best_video_link = f"{best_snippet['video_link']}&t={best_timestamp}s"

    # Generate OpenAI response
    chat_prompt = f"""
    You are a legal chatbot assistant specializing in immigration law. 
    Use the following transcript snippets to answer user queries:

    User Question: {query}
    
    Podcast Transcript:
    {full_transcript_text}
    
    Provide an answer referencing relevant timestamps.
    """

    client = openai.OpenAI(api_key="YOUR_OPENAI_API_KEY")  # Replace with your actual key

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