import { useEffect, useState } from "react";
import { api } from "../api";
import CategoryEditor from "./CategoryEditor.jsx";

const TIME_FILTERS = ["hour", "day", "week", "month", "year", "all"];

export default function Reddit() {
  const [categories, setCategories] = useState([]);
  const [sources, setSources] = useState([]);
  const [searches, setSearches] = useState([]);
  const [error, setError] = useState("");
  const [ready, setReady] = useState(false);
  const [categoryName, setCategoryName] = useState("");
  const [subreddit, setSubreddit] = useState("");
  const [sourceCategory, setSourceCategory] = useState("");
  const [query, setQuery] = useState("");
  const [searchCategory, setSearchCategory] = useState("");
  const [timeFilter, setTimeFilter] = useState("week");
  const [openCategory, setOpenCategory] = useState(null);

  const hasCategories = categories.length > 0;
  const locked = !ready || !hasCategories;

  async function load() {
    const [cats, src, q] = await Promise.all([
      api.categories(),
      api.sources(),
      api.searches(),
    ]);
    setCategories(cats);
    setSources(src);
    setSearches(q);
    if (cats.length && !sourceCategory) setSourceCategory(String(cats[0].id));
    if (cats.length && !searchCategory) setSearchCategory(String(cats[0].id));
    setReady(true);
  }

  useEffect(() => {
    load().catch((err) => {
      setError(err.message);
      setReady(true);
    });
  }, []);

  async function run(action) {
    setError("");
    try {
      await action();
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section>
      <div className="page-head">
        <div>
          <h2>Reddit sources</h2>
          <p>Create a category first. Subreddits and searches stay locked until then.</p>
        </div>
      </div>

      {error ? <p className="error">{error}</p> : null}
      {ready && !hasCategories ? (
        <div className="banner">
          Add at least one category (RhoQ, ThoughtSpace, Job, AI, …). Subreddits and
          search queries stay disabled until you do.
        </div>
      ) : null}

      <div className="card" style={{ marginBottom: 16 }}>
        <h3>Categories</h3>
        <form
          className="form inline"
          onSubmit={(e) => {
            e.preventDefault();
            run(async () => {
              await api.createCategory({ name: categoryName });
              setCategoryName("");
            });
          }}
        >
          <label>
            New category
            <input
              value={categoryName}
              onChange={(e) => setCategoryName(e.target.value)}
              placeholder="e.g. RhoQ"
              required
            />
          </label>
          <button className="btn" type="submit">
            Add category
          </button>
        </form>
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Active</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {categories.map((cat) => (
              <tr key={cat.id}>
                <td>{cat.name}</td>
                <td>{cat.active === false ? "no" : "yes"}</td>
                <td>
                  <button
                    className="btn ghost"
                    onClick={() =>
                      setOpenCategory(openCategory === cat.id ? null : cat.id)
                    }
                  >
                    {openCategory === cat.id ? "Close" : "Edit"}
                  </button>
                  <button
                    className="btn danger"
                    style={{ marginLeft: 8 }}
                    onClick={() => run(() => api.deleteCategory(cat.id))}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {categories
          .filter((cat) => cat.id === openCategory)
          .map((cat) => (
            <CategoryEditor
              key={cat.id}
              category={cat}
              onSave={(body) =>
                run(async () => {
                  await api.updateCategory(cat.id, body);
                  setOpenCategory(null);
                })
              }
            />
          ))}
      </div>

      <div className={`disabled-block ${locked ? "is-off" : ""}`}>
        <div className="card" style={{ marginBottom: 16 }}>
          <h3>Subreddits</h3>
          <form
            className="form"
            onSubmit={(e) => {
              e.preventDefault();
              if (!sourceCategory) {
                setError("Pick a category for this subreddit");
                return;
              }
              run(async () => {
                await api.createSource({
                  subreddit,
                  category_id: Number(sourceCategory),
                });
                setSubreddit("");
              });
            }}
          >
            <label>
              Subreddit
              <input
                value={subreddit}
                onChange={(e) => setSubreddit(e.target.value)}
                placeholder="fitness"
                required
                disabled={locked}
              />
            </label>
            <label>
              Category (required)
              <select
                value={sourceCategory}
                onChange={(e) => setSourceCategory(e.target.value)}
                required
                disabled={locked}
              >
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </label>
            <button className="btn" type="submit" disabled={locked}>
              Add subreddit
            </button>
          </form>
          <table className="table">
            <thead>
              <tr>
                <th>Subreddit</th>
                <th>Category</th>
                <th>Active</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {sources.map((row) => (
                <tr key={row.id}>
                  <td>r/{row.subreddit}</td>
                  <td>{row.category_name}</td>
                  <td>{row.active ? "yes" : "no"}</td>
                  <td>
                    <button
                      className="btn ghost"
                      onClick={() =>
                        run(() => api.updateSource(row.id, { active: !row.active }))
                      }
                    >
                      {row.active ? "Pause" : "Activate"}
                    </button>
                    <button
                      className="btn danger"
                      style={{ marginLeft: 8 }}
                      onClick={() => run(() => api.deleteSource(row.id))}
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card">
          <h3>Search queries</h3>
          <form
            className="form"
            onSubmit={(e) => {
              e.preventDefault();
              if (!searchCategory) {
                setError("Pick a category for this search");
                return;
              }
              run(async () => {
                await api.createSearch({
                  query,
                  category_id: Number(searchCategory),
                  time_filter: timeFilter,
                });
                setQuery("");
              });
            }}
          >
            <label>
              Search
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="fitness community"
                required
                disabled={locked}
              />
            </label>
            <label>
              Category (required)
              <select
                value={searchCategory}
                onChange={(e) => setSearchCategory(e.target.value)}
                required
                disabled={locked}
              >
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Time filter
              <select
                value={timeFilter}
                onChange={(e) => setTimeFilter(e.target.value)}
                disabled={locked}
              >
                {TIME_FILTERS.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </label>
            <button className="btn" type="submit" disabled={locked}>
              Add search
            </button>
          </form>
          <table className="table">
            <thead>
              <tr>
                <th>Query</th>
                <th>Time</th>
                <th>Category</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {searches.map((row) => (
                <tr key={row.id}>
                  <td>{row.query}</td>
                  <td>{row.time_filter}</td>
                  <td>{row.category_name}</td>
                  <td>
                    <button
                      className="btn danger"
                      onClick={() => run(() => api.deleteSearch(row.id))}
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
