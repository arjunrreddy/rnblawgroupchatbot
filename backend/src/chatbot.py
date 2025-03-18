from fastapi import FastAPI, Query
import sys
import os
import json
from openai import OpenAI
from search import search_transcript, get_most_relevant_timestamp
import yaml

# Ensure the `src/` folder is included in Python's path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Load API key from config.yaml
def load_config():
    with open("config/config.yaml", "r") as file:
        return yaml.safe_load(file)

config = load_config()
api_key = config.get("openai_api_key", None)

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Immigration AI Chatbot!"}

@app.get("/ask")
def ask_question(query: str = Query(..., description="Ask a question about immigration updates")):
    # Get relevant transcript excerpts
    search_results = search_transcript(query, top_k=5)

    # Extract transcript text
    full_transcript_text = "\n".join([f"({result['timestamp']}s) {result['answer']}" for result in search_results])
    
    # Find the best timestamp and video link
    best_timestamp, best_video_link = get_most_relevant_timestamp(search_results)

    # If no results, return an error response
    if not search_results or not best_video_link:
        return {
            "response": "I'm sorry, but I couldn't find anything relevant in the podcast transcript. Try rewording your question.",
            "references": "No relevant video sections found."
        }

    # Ensure video link is formatted correctly
    best_video_link = f"{best_video_link}&t={best_timestamp}s"

    # Create a structured prompt for ChatGPT
    chat_prompt = (
        "You are a legal news AI assistant specializing in immigration law. "
        "You have access to a podcast transcript where immigration attorneys discuss new policies.\n\n"
        "Your task is to answer the user's question using:\n"
        "- Your knowledge of immigration law\n"
        "- Key insights from the podcast transcript\n\n"
        f"User's Question: {query}\n\n"
        "Podcast Transcript Insights:\n"
        f"{full_transcript_text}\n\n"
        "Your answer should:\n"
        "- Provide a direct, professional response\n"
        "- Include insights from the podcast as supporting evidence\n"
        "- Reference the most relevant video section naturally\n"
        "- Conclude with a call-to-action, encouraging the user to watch the video."
    )

    try:
        # Generate response using ChatGPT with full transcript context
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI assistant integrating immigration law insights from a podcast."},
                {"role": "user", "content": chat_prompt}
            ],
        )
        chat_response = response.choices[0].message.content
    except Exception as e:
        chat_response = f"❌ Error generating AI response: {e}"

    # Format final response
    final_response = {
        "response": chat_response,
        "references": f"For more details, watch this part of the podcast: {best_video_link} (at {best_timestamp}s)."
    }

    return final_response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)