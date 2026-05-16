import "./App.css";
import storyJson from "./data/katmanlar.json";
import type { Story } from "./types";
import { Cosmos } from "./components/Cosmos";
import { ProgressBar } from "./components/ProgressBar";
import { SideNav } from "./components/SideNav";
import { Hero } from "./components/Hero";
import { SectionView } from "./components/Section";
import { Footer } from "./components/Footer";

const story = storyJson as Story;

function App() {
  return (
    <div className="app">
      <Cosmos />
      <ProgressBar />
      <SideNav sections={story.sections} />

      <Hero title={story.title} subtitle={story.subtitle} />

      <main>
        {story.sections.map((s, i) => (
          <SectionView key={s.id} section={s} index={i} />
        ))}
      </main>

      <Footer />
    </div>
  );
}

export default App;
