import { useState } from "react";
import "./App.css";
import storyJson from "./data/katmanlar.json";
import type { Story } from "./types";
import { useLenis } from "./hooks/useLenis";
import { useScrollProgressRef } from "./hooks/useScrollProgress";
import { Loader } from "./components/Loader";
import { Stage } from "./three/Stage";
import { TextOverlay } from "./components/TextOverlay";

const story = storyJson as Story;

function App() {
  useLenis();
  const scroll = useScrollProgressRef();
  const [ready, setReady] = useState(false);

  return (
    <div className="app">
      <Loader onDone={() => setReady(true)} />

      <div className="cosmos-bg" aria-hidden="true">
        <div className="grain" />
      </div>

      {/* Real 3D stage fixed to viewport */}
      {ready && <Stage scroll={scroll} />}

      {/* Text overlay scrolls over the 3D stage */}
      <TextOverlay story={story} />

      <footer className="story-foot">
        <div className="story-foot__byline">
          Bilirubin 28. Yıldız hâlâ ışığın altında.
        </div>
        <div className="story-foot__meta">
          Yıldız'ın Sarılığı · 21 katman · 3D scrollytelling
        </div>
      </footer>
    </div>
  );
}

export default App;
