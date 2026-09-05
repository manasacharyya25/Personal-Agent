import { useEffect, useState } from "react";
import { api } from "../api";

function formatScore(value) {
  const n = Number(value);
  if (Number.isNaN(n)) return "—";
  return n.toFixed(2);
}

export default function Overview() {
  const [categories, setCategories] = useState([]);
  const [posts, setPosts] = useState([]);
  const [categoryId, setCategoryId] = useState("");
  const [openId, setOpenId] = useState(null);
  const [error, setError] = useState("");
  const [ready, setReady] = useState(false);

  async function load(nextCategory = categoryId) {
    setError("");
    const params = { limit: 100 };
    if (nextCategory) params.category_id = nextCategory;
    const cats = await api.categories();
    setCategories(cats);
    const rows = await api.evaluations(params);
    setPosts(rows);
    setReady(true);
  }

  useEffect(() => {
    load().catch((err) => {
      setError(err.message);
      setReady(true);
    });
  }, []);

  return (
    <section>
      <div className="page-head">
        <div>
          <h2>Overview</h2>
          <p>Posts ranked by evaluator score. Highest first.</p>
        </div>
        <span className="pill ok">{posts.length} scored</span>
      </div>

      {error ? <p className="error">{error}</p> : null}

      <div className="card" style={{ marginBottom: 16 }}>
        <form className="form inline" onSubmit={(e) => e.preventDefault()}>
          <label>
            Category
            <select
              value={categoryId}
              onChange={(e) => {
                const next = e.target.value;
                setCategoryId(next);
                setError("");
                load(next).catch((err) => setError(err.message));
              }}
            >
              <option value="">All categories</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
          </label>
        </form>
      </div>

      {ready && !error && posts.length === 0 ? (
        <div className="banner">
          No scored posts yet. Run the evaluator, then refresh this page.
        </div>
      ) : null}

      <div className="list">
        {posts.map((post) => {
          const open = openId === post.id;
          const scores = post.scores && typeof post.scores === "object" ? post.scores : {};
          return (
            <article className="card post-card" key={post.id}>
              <div className="post-head">
                <div className="stat">{formatScore(post.mean_score)}</div>
                <div>
                  <h3>{post.title || "(no title)"}</h3>
                  <p className="muted">
                    {post.category_name}
                    {post.subreddit ? ` · r/${post.subreddit}` : ""}
                    {post.author ? ` · u/${post.author}` : ""}
                  </p>
                </div>
              </div>
              {post.reason ? <p className="post-reason">{post.reason}</p> : null}
              {Object.keys(scores).length ? (
                <div className="score-pills">
                  {Object.entries(scores).map(([key, value]) => (
                    <span className="pill" key={key}>
                      {key} {formatScore(value)}
                    </span>
                  ))}
                </div>
              ) : null}
              <div className="post-actions">
                <button
                  type="button"
                  className="btn ghost"
                  onClick={() => setOpenId(open ? null : post.id)}
                >
                  {open ? "Hide body" : "Show body"}
                </button>
                {post.url ? (
                  <a className="btn ghost" href={post.url} target="_blank" rel="noreferrer">
                    Open post
                  </a>
                ) : null}
              </div>
              {open && post.body ? <pre className="post-body">{post.body}</pre> : null}
              {open && !post.body ? <p className="muted">No body stored for this post.</p> : null}
            </article>
          );
        })}
      </div>
    </section>
  );
}
