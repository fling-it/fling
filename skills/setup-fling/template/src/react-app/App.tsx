import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [message, setMessage] = useState<string>("Loading...");

  useEffect(() => {
    fetch("/api/hello")
      .then((res) => res.json())
      .then((data: { message: string }) => setMessage(data.message))
      .catch(() => setMessage("Failed to connect to API"));
  }, []);

  return (
    <div className="app">
      <h1>Fling App</h1>
      <p className="api-message">{message}</p>
      <p className="hint">
        Edit <code>src/react-app/App.tsx</code> for the frontend
        <br />
        Edit <code>src/worker/index.ts</code> for the API
      </p>
    </div>
  );
}

export default App;
