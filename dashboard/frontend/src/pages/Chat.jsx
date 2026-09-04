import { useEffect, useState } from "react";

const STARTERS = [
  "Draft an onboarding note for a RhoQ-curious fitness creator.",
  "Is this Reddit job a fit for my skills?",
  "Summarize why this ThoughtSpace thread is a lead.",
];

export default function Chat() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "agent",
      text: "Chat is mocked for now. Later this thread will use knowledge bases and a selected Reddit post.",
    },
  ]);

  function send(text) {
    const value = (text || input).trim();
    if (!value) return;
    setMessages((current) => [
      ...current,
      { role: "user", text: value },
      {
        role: "agent",
        text: "Mock reply. When the agent is wired, this will search RhoQ / ThoughtSpace / skills and draft a message for one post.",
      },
    ]);
    setInput("");
  }

  return (
    <section>
      <div className="page-head">
        <div>
          <h2>Agent chat</h2>
          <p>Standalone thread. Per-post drafts come after the evaluator.</p>
        </div>
        <span className="pill warn">Mock</span>
      </div>
      <div className="chat-wrap">
        <div className="messages">
          {messages.map((msg, i) => (
            <div key={i} className={`bubble ${msg.role}`}>
              {msg.text}
            </div>
          ))}
          <div className="muted" style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {STARTERS.map((hint) => (
              <button key={hint} className="btn ghost" onClick={() => send(hint)}>
                {hint}
              </button>
            ))}
          </div>
        </div>
        <form
          className="composer"
          onSubmit={(e) => {
            e.preventDefault();
            send();
          }}
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask the agent…"
          />
          <button className="btn" type="submit">
            Send
          </button>
        </form>
      </div>
    </section>
  );
}
