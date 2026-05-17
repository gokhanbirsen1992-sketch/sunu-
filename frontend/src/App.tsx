import "./App.css";
import storyJson from "./data/katmanlar.json";
import type { Story } from "./types";
import { useLenis } from "./hooks/useLenis";
import { CinematicHero } from "./components/CinematicHero";
import { CinematicJourney } from "./components/CinematicJourney";

const story = storyJson as Story;

function App() {
  useLenis();

  return (
    <div className="app">
      <div className="cosmos-bg" aria-hidden="true">
        <div className="cosmos-stars" />
        <div className="cosmos-tint-a" />
        <div className="cosmos-tint-b" />
        <div className="grain" />
      </div>

      <CinematicHero title={story.title} subtitle={story.subtitle} />

      <CinematicJourney story={story} />

      <footer className="story-foot">
        <div className="story-foot__byline">
          Bilirubin 28. Yıldız hâlâ ışığın altında.
        </div>
        <div className="story-foot__meta">
          Yıldız'ın Sarılığı · 21 katman · cinematic
        </div>
      </footer>
    </div>
  );
}

export default App;
