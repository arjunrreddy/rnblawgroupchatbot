import React, { useState, useRef, useEffect } from "react";
import "./App.css";

// 🔁 Change this to your ngrok URL or localhost
//const BACKEND_URL = "https://daa3-70-122-236-70.ngrok-free.app";
const BACKEND_URL = "http://127.0.0.1:8000"; // ⬅️ Use this line if you're testing locally

function App() {
  const [query, setQuery] = useState("");
  const [userQuestion, setUserQuestion] = useState("");
  const [response, setResponse] = useState(null);
  const [timestamp, setTimestamp] = useState(null);
  const videoRef = useRef(null);

  const handleAskQuestion = async () => {
    if (!query.trim()) return;

    setUserQuestion(query);
    setQuery("");

    try {
      const res = await fetch(`${BACKEND_URL}/ask?query=${encodeURIComponent(query)}`);
      const data = await res.json();

      setResponse(data.response || "No response available.");
      setTimestamp(data.timestamp || null);
    } catch (error) {
      console.error("Error fetching response:", error);
      setResponse("Error retrieving response. Please try again.");
    }
  };

  useEffect(() => {
    if (timestamp !== null && videoRef.current) {
      videoRef.current.currentTime = timestamp;
    }
  }, [timestamp]);

  return (
    <div className="App">
      <h1>Immigration Law Chatbot</h1>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask your immigration question..."
      />
      <button onClick={handleAskQuestion}>Ask</button>

      {response && (
        <div>
          {userQuestion && <h3><strong>Q: {userQuestion}</strong></h3>}

          <h3>Response:</h3>
          <p>{response}</p>

          {timestamp !== null && (
            <div>
              <h4>Relevant Video Section:</h4>
              <video controls width="600" ref={videoRef}>
                <source src={`${BACKEND_URL}/video`} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
              <p>
                <strong>Jump to:</strong> {timestamp} seconds
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;