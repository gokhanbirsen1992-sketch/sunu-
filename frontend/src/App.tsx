import "./App.css";
import storyJson from "./data/katmanlar.json";
import type { MotionValue } from "framer-motion";
import type { Section, Story } from "./types";
import { useLenis } from "./hooks/useLenis";
import { CinematicHero } from "./components/CinematicHero";
import { ScrollScene } from "./components/ScrollScene";
import { SceneDivider } from "./components/SceneDivider";
import { ProgressRail } from "./components/ProgressRail";
import { NARRATIVE_ORDER } from "./data/nodeLayout";
import { AmbientVisual } from "./scenes/AmbientVisual";
import { CosmosVisual } from "./scenes/CosmosVisual";
import { BilirubinVisual } from "./scenes/BilirubinVisual";
import { HepatocyteVisual } from "./scenes/HepatocyteVisual";
import { ClosureVisual } from "./scenes/ClosureVisual";
import { EmbriyolojiVisual } from "./scenes/EmbriyolojiVisual";
import { PatofizyolojiVisual } from "./scenes/PatofizyolojiVisual";
import { YildizVakasiVisual } from "./scenes/YildizVakasiVisual";
import { AlgoritmaVisual } from "./scenes/AlgoritmaVisual";

const story = storyJson as Story;

const SCENE_VISUALS: Record<
  string,
  React.ComponentType<{ progress: MotionValue<number> }>
> = {
  "1": CosmosVisual,
  "2": BilirubinVisual,
  "3": HepatocyteVisual,
  "5": EmbriyolojiVisual,
  "11": PatofizyolojiVisual,
  "12.1": YildizVakasiVisual,
  "12.7": AlgoritmaVisual,
  "13": ClosureVisual,
};

function visualFor(id: string) {
  const Bespoke = SCENE_VISUALS[id];
  if (Bespoke) return Bespoke;
  return ({ progress }: { progress: MotionValue<number> }) => (
    <AmbientVisual id={id} progress={progress} />
  );
}

const sectionsById: Record<string, Section> = {};
for (const s of story.sections) sectionsById[s.id] = s;

function App() {
  useLenis();

  return (
    <div className="app">
      <div className="cosmos-bg" aria-hidden="true">
        <div className="cosmos-stars" />
        <div className="cosmos-tint-a" />
        <div className="cosmos-tint-b" />
      </div>

      <ProgressRail />

      <CinematicHero title={story.title} subtitle={story.subtitle} />

      <main className="story">
        {NARRATIVE_ORDER.map((id, i) => {
          const section = sectionsById[id];
          if (!section) return null;
          const prev = NARRATIVE_ORDER[i - 1];
          return (
            <div key={id}>
              {prev && <SceneDivider fromId={prev} toId={id} />}
              <ScrollScene section={section} Visual={visualFor(id)} />
            </div>
          );
        })}
      </main>

      <footer className="story-foot">
        <div className="story-foot__byline">
          Bilirubin 28. Yıldız hâlâ ışığın altında.
        </div>
        <div className="story-foot__meta">
          Yıldız'ın Sarılığı · 21 katman · scrollytelling
        </div>
      </footer>
    </div>
  );
}

export default App;
