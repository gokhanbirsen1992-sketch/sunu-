import { useEffect, useState } from "react";
import "./App.css";
import storyJson from "./data/katmanlar.json";
import type { Story } from "./types";
import { useLenis } from "./hooks/useLenis";
import { Loader } from "./components/Loader";
import { PhotoStage } from "./components/PhotoStage";
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
  const [loaded, setLoaded] = useState(false);
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <div className="app">
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
          {mounted ? "ready" : "mounting..."}
        </div>
      )}

      <Loader onDone={() => setLoaded(true)} />

      <ErrorBoundary label="Photo Stage">
        <PhotoStage />
      </ErrorBoundary>

      <ErrorBoundary label="Text Overlay">
        <TextOverlay story={story} />
      </ErrorBoundary>

      <footer className="story-foot">
        <div className="story-foot__byline">
          Bilirubin 28. Yıldız hâlâ ışığın altında.
        </div>
        <div className="story-foot__meta">
          Yıldız'ın Sarılığı · 21 katman · görseller OpenStax Biology (CC-BY)
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
