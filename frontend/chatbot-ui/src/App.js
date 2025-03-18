import React, { useState } from "react";
import axios from "axios";

function App() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [videoLink, setVideoLink] = useState("");

  const askQuestion = async () => {
    setResponse("Thinking...");
    setVideoLink("");

    try {
      const res = await axios.get(`http://localhost:8000/ask?query=${encodeURIComponent(query)}`);
      setResponse(res.data.response);

      if (res.data.references.includes("https://")) {
        setVideoLink(res.data.references);
      }
    } catch (error) {
      setResponse("Error retrieving response. Please try again.");
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>Immigration Law Chatbot</h1>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask a question about immigration law..."
        style={{
          width: "60%",
          padding: "10px",
          fontSize: "16px",
          borderRadius: "5px",
          border: "1px solid #ccc",
        }}
      />
      <button
        onClick={askQuestion}
        style={{
          marginLeft: "10px",
          padding: "10px 15px",
          fontSize: "16px",
          backgroundColor: "#007bff",
          color: "white",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer",
        }}
      >
        Ask
      </button>
      <div id="response" style={{ marginTop: "20px", fontSize: "18px" }}>{response}</div>
      {videoLink && (
        <iframe
          title="Podcast Video"
          width="560"
          height="315"
          src={videoLink}
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          style={{ marginTop: "20px" }}
        />
      )}
    </div>
  );
}

export default App;
