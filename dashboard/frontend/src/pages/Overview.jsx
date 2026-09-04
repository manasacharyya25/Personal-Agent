const PIPELINE = ["Extraction", "DB", "Evaluator", "Notify you", "Agent"];

const REDDIT = [
  { label: "RhoQ leads", value: "12", note: "Fitness community / creators" },
  { label: "Job posts", value: "7", note: "Match vs your skills.md" },
  { label: "AI / SMB", value: "4", note: "Agentic workflow interest" },
];

const PLATFORMS = [
  {
    title: "LinkedIn / Upwork",
    items: ["Jobs to apply", "Posts worth restacking on X"],
  },
  {
    title: "Instagram",
    items: ["RhoQ-interested users", "Fitness creators to approach", "Posts for X"],
  },
  {
    title: "X",
    items: ["Replies due", "Scheduled posts", "Engagement by time"],
  },
  {
    title: "Slack → WhatsApp",
    items: ["Important threads flagged", "Nothing sent until you confirm"],
  },
  {
    title: "Vercel / Supabase",
    items: ["Traffic deltas", "New signups / plans / posts / lives"],
  },
];

export default function Overview() {
  return (
    <section>
      <div className="page-head">
        <div>
          <h2>Overview</h2>
          <p>Mock snapshot of the Handoff pipeline. Evaluator and other platforms are not live yet.</p>
        </div>
        <span className="pill warn">Mock data</span>
      </div>

      <div className="pipeline">
        {PIPELINE.map((step) => (
          <div className="pipe" key={step}>
            {step}
          </div>
        ))}
      </div>

      <div className="grid cols-2">
        <div className="card">
          <h3>Latest Reddit ingestion</h3>
          <div className="pill">completed · 8 min ago</div>
          <p className="muted" style={{ marginTop: 12 }}>
            84 posts seen · 31 new · Chromium closed after the job.
          </p>
        </div>
        <div className="card">
          <h3>Evaluator</h3>
          <div className="list">
            <div className="row-item">
              <span>Job ↔ skills</span>
              <span className="stat">7</span>
            </div>
            <div className="row-item">
              <span>Lead ↔ RhoQ / ThoughtSpace</span>
              <span className="stat">16</span>
            </div>
            <div className="row-item">
              <span>Content scoring</span>
              <span className="stat">9</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid cols-3" style={{ marginTop: 16 }}>
        {REDDIT.map((item) => (
          <div className="card" key={item.label}>
            <h3>Reddit · {item.label}</h3>
            <div className="stat">{item.value}</div>
            <p className="muted">{item.note}</p>
          </div>
        ))}
      </div>

      <div className="grid cols-2" style={{ marginTop: 16 }}>
        {PLATFORMS.map((block) => (
          <div className="card" key={block.title}>
            <h3>{block.title}</h3>
            <div className="list">
              {block.items.map((item) => (
                <div className="row-item" key={item}>
                  <span>{item}</span>
                  <span className="muted">—</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
