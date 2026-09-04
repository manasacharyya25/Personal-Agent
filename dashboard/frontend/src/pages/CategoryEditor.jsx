import { useState } from "react";

function slug(label) {
  return label
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_|_$/g, "")
    .slice(0, 80) || "criterion";
}

function emptyMetric() {
  return { key: "", label: "", definition: "" };
}

export default function CategoryEditor({ category, onSave }) {
  const [purpose, setPurpose] = useState(category.purpose || "");
  const [prompt, setPrompt] = useState(category.prompt || "");
  const [examples, setExamples] = useState(category.examples || "");
  const [active, setActive] = useState(category.active !== false);
  const [metrics, setMetrics] = useState(
    category.evaluation_metrics?.length
      ? category.evaluation_metrics
      : [emptyMetric()]
  );

  function setMetric(index, field, value) {
    setMetrics((current) =>
      current.map((row, i) => {
        if (i !== index) return row;
        const next = { ...row, [field]: value };
        if (field === "label") next.key = slug(value);
        return next;
      })
    );
  }

  function submit(e) {
    e.preventDefault();
    onSave({
      purpose,
      prompt,
      examples,
      active,
      evaluation_metrics: metrics
        .filter((row) => row.label.trim() && row.definition.trim())
        .map((row) => ({
          key: row.key || slug(row.label),
          label: row.label.trim(),
          definition: row.definition.trim(),
        })),
    });
  }

  return (
    <form className="form" onSubmit={submit} style={{ marginTop: 12 }}>
      <label>
        <span>
          Active
          <input
            type="checkbox"
            checked={active}
            onChange={(e) => setActive(e.target.checked)}
            style={{ marginLeft: 8 }}
          />
        </span>
      </label>
      <label>
        Purpose
        <textarea
          value={purpose}
          onChange={(e) => setPurpose(e.target.value)}
          placeholder="Why this category exists"
          rows={2}
        />
      </label>
      <label>
        Evaluator prompt
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Check if the post is about someone looking for a workout plan"
          rows={3}
        />
      </label>
      <label>
        Examples
        <textarea
          value={examples}
          onChange={(e) => setExamples(e.target.value)}
          placeholder="Good: … / Bad: …"
          rows={3}
        />
      </label>
      <div>
        <div className="muted" style={{ marginBottom: 8 }}>
          Criteria (mean of 0–5 scores)
        </div>
        {metrics.map((row, index) => (
          <div className="metric-row" key={index}>
            <input
              value={row.label}
              onChange={(e) => setMetric(index, "label", e.target.value)}
              placeholder="Criterion"
            />
            <input
              value={row.definition}
              onChange={(e) => setMetric(index, "definition", e.target.value)}
              placeholder="Definition"
            />
            <button
              type="button"
              className="btn ghost"
              onClick={() =>
                setMetrics((current) => current.filter((_, i) => i !== index))
              }
            >
              ×
            </button>
          </div>
        ))}
        <button
          type="button"
          className="btn ghost"
          onClick={() => setMetrics((current) => [...current, emptyMetric()])}
        >
          Add criterion
        </button>
      </div>
      <button className="btn" type="submit">
        Save category
      </button>
    </form>
  );
}
