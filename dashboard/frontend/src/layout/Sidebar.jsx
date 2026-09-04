const NAV = [
  { id: "overview", label: "Overview" },
  { id: "reddit", label: "Reddit" },
  { id: "chat", label: "Chat" },
];

const LATER = [
  { id: "linkedin", label: "LinkedIn / Upwork" },
  { id: "instagram", label: "Instagram" },
  { id: "x", label: "X" },
  { id: "slack", label: "Slack" },
  { id: "ops", label: "Vercel / Supabase" },
];

export default function Sidebar({ view, onChange }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-kicker">Personal agent</div>
        <h1>Control</h1>
      </div>
      <nav className="nav">
        <div className="nav-label">Now</div>
        {NAV.map((item) => (
          <button
            key={item.id}
            className={`nav-btn ${view === item.id ? "active" : ""}`}
            onClick={() => onChange(item.id)}
          >
            {item.label}
          </button>
        ))}
        <div className="nav-label">Later</div>
        {LATER.map((item) => (
          <button key={item.id} className="nav-btn" disabled>
            {item.label}
            <span className="nav-soon">soon</span>
          </button>
        ))}
      </nav>
    </aside>
  );
}
