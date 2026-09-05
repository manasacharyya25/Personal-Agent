import { useState } from "react";

export default function CategoryEditor({ category, onSave }) {
  const [purpose, setPurpose] = useState(category.purpose || "");
  const [prompt, setPrompt] = useState(category.prompt || "");
  const [examples, setExamples] = useState(category.examples || "");
  const [active, setActive] = useState(category.active !== false);

  function submit(e) {
    e.preventDefault();
    onSave({
      purpose,
      prompt,
      examples,
      active,
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
          placeholder="How to score this post"
          rows={8}
        />
      </label>
      <label>
        Examples
        <textarea
          value={examples}
          onChange={(e) => setExamples(e.target.value)}
          placeholder="Good: … / Bad: …"
          rows={4}
        />
      </label>
      <button className="btn" type="submit">
        Save category
      </button>
    </form>
  );
}
