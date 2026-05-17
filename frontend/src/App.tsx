import { useState } from "react";
import "./App.css";
import storyJson from "./data/katmanlar.json";
import type { Story } from "./types";
import { useLenis } from "./hooks/useLenis";
import { useScrollProgressRef } from "./hooks/useScrollProgress";
import { Loader } from "./components/Loader";
import { Stage } from "./three/Stage";
import { TextOverlay } from "./components/TextOverlay";
import { ErrorBoundary } from "./components/ErrorBoundary";

const story = storyJson as Story;

function App() {
  useLenis();
  const scroll = useScrollProgressRef();
  const [loaded, setLoaded] = useState(false);

  return (
    <div className="app">
      <Loader onDone={() => setLoaded(true)} />

      <div className="cosmos-bg" aria-hidden="true">
        <div className="grain" />
      </div>

      {/* 3D stage renders immediately; loader fades over it */}
      <ErrorBoundary
        fallback={
          <div
            style={{
              position: "fixed",
              inset: 0,
              display: "grid",
              placeItems: "center",
              fontFamily: "system-ui",
              fontSize: 14,
              color: "#fecaca",
              padding: 24,
              textAlign: "center",
              zIndex: 1,
            }}
          >
            3D motor yüklenemedi. Tarayıcı WebGL desteklemiyor olabilir.
          </div>
        }
      >
        <Stage scroll={scroll} effects={false} />
      </ErrorBoundary>

      <TextOverlay story={story} />

      <footer className="story-foot">
        <div className="story-foot__byline">
          Bilirubin 28. Yıldız hâlâ ışığın altında.
        </div>
        <div className="story-foot__meta">
          Yıldız'ın Sarılığı · 21 katman · 3D scrollytelling
          {!loaded && <span style={{ opacity: 0.4 }}> · loading</span>}
        </div>
      </footer>
    </div>
  );
}

export default App;
