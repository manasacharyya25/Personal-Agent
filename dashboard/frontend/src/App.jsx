import { useState } from "react";
import Sidebar from "./layout/Sidebar.jsx";
import Overview from "./pages/Overview.jsx";
import Reddit from "./pages/Reddit.jsx";
import Chat from "./pages/Chat.jsx";

export default function App() {
  const [view, setView] = useState("overview");

  return (
    <div className="shell">
      <Sidebar view={view} onChange={setView} />
      <main className="main">
        {view === "overview" ? <Overview /> : null}
        {view === "reddit" ? <Reddit /> : null}
        {view === "chat" ? <Chat /> : null}
      </main>
    </div>
  );
}
