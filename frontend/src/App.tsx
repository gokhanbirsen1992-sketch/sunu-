import { useEffect, useState } from "react";
import "./App.css";
import storyJson from "./data/katmanlar.json";
import type { Story } from "./types";
import { Hub } from "./components/Hub";
import { KatmanModal } from "./components/KatmanModal";

const story = storyJson as Story;

function App() {
  const [activeId, setActiveId] = useState<string | null>(null);

  // Prevent body scroll while modal is open
  useEffect(() => {
    if (activeId) {
      const prev = document.body.style.overflow;
      document.body.style.overflow = "hidden";
      return () => {
        document.body.style.overflow = prev;
      };
    }
  }, [activeId]);

  return (
    <div className="app">
      <Hub story={story} onSelect={setActiveId} />
      <KatmanModal
        story={story}
        activeId={activeId}
        onClose={() => setActiveId(null)}
        onNavigate={setActiveId}
      />
    </div>
  );
}

export default App;
