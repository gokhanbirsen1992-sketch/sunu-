import { motion, useScroll, useTransform, type MotionValue } from "framer-motion";
import { layerTheme } from "../layerThemes";
import { NARRATIVE_ORDER } from "../data/nodeLayout";

type ScenePlan =
  | { kind: "image"; src: string; alt: string; focal?: "center" | "top" | "bottom" }
  | { kind: "card" };

const BASE = import.meta.env.BASE_URL;

const SCENES: Record<string, ScenePlan> = {
  "1": { kind: "card" },
  "2": { kind: "image", src: `${BASE}scenes/02-bilirubin.jpg`, alt: "Protein / molecule structure (OpenStax, CC-BY)" },
  "3": { kind: "image", src: `${BASE}scenes/03-hucresel.jpg`, alt: "Eukaryotic cell anatomy (OpenStax, CC-BY)" },
  "4": { kind: "image", src: `${BASE}scenes/04-evrim.jpg`, alt: "Evolution concept (OpenStax, CC-BY)" },
  "5": { kind: "image", src: `${BASE}scenes/05-embriyoloji.jpg`, alt: "Early embryo development (OpenStax, CC-BY)" },
  "6": { kind: "card" },
  "7": { kind: "image", src: `${BASE}scenes/07-anatomi.jpg`, alt: "Digestive anatomy with liver (OpenStax, CC-BY)" },
  "8": { kind: "image", src: `${BASE}scenes/08-histoloji.jpg`, alt: "Cell membrane structure (OpenStax, CC-BY)" },
  "9": { kind: "image", src: `${BASE}scenes/09-fizyoloji.png`, alt: "Lipid digestion pathway (OpenStax, CC-BY)" },
  "10": { kind: "image", src: `${BASE}scenes/10-biyokimya.jpg`, alt: "Enzyme structure (OpenStax, CC-BY)" },
  "11": { kind: "card" },
  "12.1": { kind: "image", src: `${BASE}scenes/12-1-yildiz.jpg`, alt: "Third-trimester fetus (OpenStax, CC-BY)" },
  "12.2": { kind: "card" },
  "12.3": { kind: "card" },
  "12.4": { kind: "card" },
  "12.5": { kind: "card" },
  "12.6": { kind: "card" },
  "12.7": { kind: "card" },
  "12.8": { kind: "card" },
  "12.9": { kind: "card" },
  "13": { kind: "card" },
};

/**
 * Cinematic photo essay stage. Tek sticky viewport, scroll'la sahneler
 * crossfade eder. Image sahnelerinde Ken Burns (subtle zoom + pan);
 * card sahnelerinde aksan rengi tam ekran + glyph + tagline.
 */
export function PhotoStage() {
  // Window-level scroll progress, shared with TextOverlay so both stay in sync.
  const { scrollYProgress } = useScroll();

  const seg = 1 / NARRATIVE_ORDER.length;
  const ranges = NARRATIVE_ORDER.reduce<Record<string, [number, number]>>(
    (acc, id, i) => {
      acc[id] = [i * seg, (i + 1) * seg];
      return acc;
    },
    {},
  );

  return (
    <div className="ps">
      <div className="ps__viewport">
        {NARRATIVE_ORDER.map((id) => {
          const plan = SCENES[id];
          if (!plan) return null;
          return (
            <PhotoScene
              key={id}
              id={id}
              plan={plan}
              range={ranges[id]}
              progress={scrollYProgress}
            />
          );
        })}
        <div className="ps__vignette" aria-hidden="true" />
        <div className="ps__grain" aria-hidden="true" />
      </div>
    </div>
  );
}

function PhotoScene({
  id,
  plan,
  range,
  progress,
}: {
  id: string;
  plan: ScenePlan;
  range: [number, number];
  progress: MotionValue<number>;
}) {
  const [r0, r1] = range;
  const span = r1 - r0;
  const theme = layerTheme(id);

  // Crossfade window: fade in over first 15%, fade out over last 15%
  const opacity = useTransform(
    progress,
    [r0, r0 + span * 0.12, r1 - span * 0.12, r1],
    [0, 1, 1, 0],
  );

  // Ken Burns: zoom 1.05 → 1.22 and slight pan
  const scale = useTransform(progress, [r0, r1], [1.05, 1.22]);
  const xPan = useTransform(progress, [r0, r1], ["-2%", "2%"]);
  const yPan = useTransform(progress, [r0, r1], ["1%", "-1%"]);

  if (plan.kind === "image") {
    return (
      <motion.div className="ps__scene" style={{ opacity }}>
        <motion.div
          className="ps__image-wrap"
          style={{ scale, x: xPan, y: yPan }}
        >
          <img className="ps__image" src={plan.src} alt={plan.alt} />
        </motion.div>
        <div
          className="ps__image-grade"
          aria-hidden="true"
          style={{
            background: `linear-gradient(180deg, rgba(3,4,10,0.35) 0%, transparent 40%, transparent 60%, rgba(3,4,10,0.6) 100%), radial-gradient(ellipse at center, transparent 30%, rgba(3,4,10,0.55) 100%)`,
          }}
        />
      </motion.div>
    );
  }

  // CARD: full-bleed accent color + giant glyph
  return (
    <motion.div className="ps__scene ps__card" style={{ opacity }}>
      <motion.div
        className="ps__card-bg"
        style={{
          scale,
          x: xPan,
          y: yPan,
          background: `radial-gradient(circle at 30% 40%, ${theme.accent}cc 0%, ${theme.accent}55 30%, #03040a 80%)`,
        }}
      />
      <motion.div
        className="ps__card-glyph"
        style={{ scale, color: theme.accent, opacity: useTransform(progress, [r0, r0 + span * 0.3, r1 - span * 0.2, r1], [0, 0.85, 0.85, 0]) }}
      >
        {theme.glyph}
      </motion.div>
    </motion.div>
  );
}
