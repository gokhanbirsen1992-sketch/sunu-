import "./App.css";
import storyJson from "./data/katmanlar.json";
import type { MotionValue } from "framer-motion";
import type { Section, Story } from "./types";
import { Cosmos } from "./components/Cosmos";
import { ProgressBar } from "./components/ProgressBar";
import { SideNav } from "./components/SideNav";
import { Hero } from "./components/Hero";
import { SectionView } from "./components/Section";
import { Scene } from "./components/Scene";
import { Footer } from "./components/Footer";
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

function renderSection(s: Section, i: number) {
  const Visual = SCENE_VISUALS[s.id];
  if (Visual) {
    return <Scene key={s.id} section={s} Visual={Visual} />;
  }
  return <SectionView key={s.id} section={s} index={i} />;
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
