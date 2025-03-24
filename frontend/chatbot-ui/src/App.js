import React, { useState, useRef, useEffect } from "react";
import "./App.css";

// 🔁 Change this to your ngrok URL or localhost
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [query, setQuery] = useState("");
  const [userQuestion, setUserQuestion] = useState("");
  const [response, setResponse] = useState(null);
  const [timestamp, setTimestamp] = useState(null);
  const videoRef = useRef(null);
  const LOCAL_BACKEND_URL = "http://127.0.0.1:8000";
  const PROD_BACKEND_URL = "https://rnblawgroupchatbot.onrender.com";

  const handleAskQuestion = async () => {
    if (!query.trim()) return;
  
    setUserQuestion(query);
    setQuery("");
  
    try {
      const res = await fetch(`${LOCAL_BACKEND_URL}/ask?query=${encodeURIComponent(query)}`);
      const data = await res.json();
      setResponse(data.response || "No response available.");
      setTimestamp(data.timestamp || null);
    } catch (err) {
      console.warn("⚠️ Local backend failed. Trying Render deployment...");
  
      try {
        const res = await fetch(`${PROD_BACKEND_URL}/ask?query=${encodeURIComponent(query)}`);
        const data = await res.json();
        setResponse(data.response || "No response available.");
        setTimestamp(data.timestamp || null);
      } catch (error) {
        console.error("❌ Both local and remote backends failed:", error);
        setResponse("Error retrieving response. Please try again later.");
      }
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
              <source src="https://www.dropbox.com/scl/fi/yz7xlp3qo3h95p4r0xtjv/march_11.mp4?rlkey=u9frr2ar77ohfhnenvkqleo0j&st=ldp6pqqo&dl=1" type="video/mp4" />
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