# React dashboard

Left sidebar: Overview, Reddit, Chat. Spec: `Implementation/phase1-dashboard.md`

```text
npm install
npm run dev
```

API: `uvicorn apps.agent.main:app --reload --app-dir ../..` from this folder is wrong.

From the repo root:

```text
uvicorn apps.agent.main:app --reload
cd dashboard/frontend && npm run dev
```

Open http://localhost:5173
