import "./App.css";
import storyJson from "./data/katmanlar.json";
import type { MotionValue } from "framer-motion";
import type { Section, Story } from "./types";
import { Cosmos } from "./components/Cosmos";
import { ProgressBar } from "./components/ProgressBar";
import { SideNav } from "./components/SideNav";
import { Hero } from "./components/Hero";
import { Scene } from "./components/Scene";
import { KatmanIntro } from "./components/KatmanIntro";
import { Footer } from "./components/Footer";
import { AmbientVisual } from "./scenes/AmbientVisual";
import { CosmosVisual } from "./scenes/CosmosVisual";
import { BilirubinVisual } from "./scenes/BilirubinVisual";
import { HepatocyteVisual } from "./scenes/HepatocyteVisual";
import { ClosureVisual } from "./scenes/ClosureVisual";

const story = storyJson as Story;

const SCENE_VISUALS: Record<
  string,
  React.ComponentType<{ progress: MotionValue<number> }>
> = {
  "1": CosmosVisual,
  "2": BilirubinVisual,
  "3": HepatocyteVisual,
  "13": ClosureVisual,
};

function renderSection(s: Section) {
  const Bespoke = SCENE_VISUALS[s.id];
  const Visual = Bespoke
    ? Bespoke
    : ({ progress }: { progress: MotionValue<number> }) => (
        <AmbientVisual id={s.id} progress={progress} />
      );
  return (
    <div key={s.id}>
      <KatmanIntro id={s.id} />
      <Scene section={s} Visual={Visual} />
    </div>
  );
}

function App() {
  return (
    <div className="app">
      <Cosmos />
      <ProgressBar />
      <SideNav sections={story.sections} />

      <Hero title={story.title} subtitle={story.subtitle} />

      <main>{story.sections.map(renderSection)}</main>

      <Footer />
    </div>
  );
}

export default App;
