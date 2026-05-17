import { useEffect, useState } from "react";
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
  return (
    <ErrorBoundary
      fallback={
        <DebugFallback message="Uygulama mount hatası — Console'a bak (F12)" />
      }
    >
      <AppInner />
    </ErrorBoundary>
  );
}

function AppInner() {
  useLenis();
  const scroll = useScrollProgressRef();
  const [loaded, setLoaded] = useState(false);
  const [mounted, setMounted] = useState(false);

  // Mark React mount succeeded
  useEffect(() => setMounted(true), []);

  return (
    <div className="app">
      {/* Diagnostic banner — visible in top-left corner. Disappears after loaded */}
      {!loaded && (
        <div
          style={{
            position: "fixed",
            top: 12,
            left: 12,
            zIndex: 9999,
            fontFamily: "system-ui, sans-serif",
            fontSize: 11,
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            color: "#d4a44b",
            background: "rgba(20, 16, 10, 0.85)",
            padding: "6px 10px",
            borderRadius: 4,
            border: "1px solid rgba(212, 164, 75, 0.3)",
            pointerEvents: "none",
          }}
        >
          {mounted ? "react ok · loading scene" : "mounting..."}
        </div>
      )}

      <Loader onDone={() => setLoaded(true)} />

      <div className="cosmos-bg" aria-hidden="true">
        <div className="grain" />
      </div>

      <ErrorBoundary>
        <Stage scroll={scroll} effects={false} />
      </ErrorBoundary>

      <ErrorBoundary>
        <TextOverlay story={story} />
      </ErrorBoundary>

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

function DebugFallback({ message }: { message: string }) {
  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        display: "grid",
        placeItems: "center",
        background: "#0a0907",
        color: "#fbf4e3",
        fontFamily: "system-ui, sans-serif",
        textAlign: "center",
        padding: 24,
      }}
    >
      <div>
        <div
          style={{
            fontSize: 11,
            letterSpacing: "0.4em",
            textTransform: "uppercase",
            color: "#d4a44b",
            marginBottom: 18,
          }}
        >
          YILDIZIN SARILIĞI
        </div>
        <div style={{ fontSize: 18, lineHeight: 1.5, opacity: 0.85 }}>
          {message}
        </div>
      </div>
    </div>
  );
}

export default App;
