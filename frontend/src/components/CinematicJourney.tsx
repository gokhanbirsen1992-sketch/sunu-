import { useRef } from "react";
import {
  motion,
  useScroll,
  useTransform,
  type MotionValue,
} from "framer-motion";
import type { Section, Story } from "../types";
import { layerTheme } from "../layerThemes";
import { AmbientVisual } from "../scenes/AmbientVisual";
import { CosmosVisual } from "../scenes/CosmosVisual";
import { BilirubinVisual } from "../scenes/BilirubinVisual";
import { HepatocyteVisual } from "../scenes/HepatocyteVisual";
import { ClosureVisual } from "../scenes/ClosureVisual";
import { EmbriyolojiVisual } from "../scenes/EmbriyolojiVisual";
import { PatofizyolojiVisual } from "../scenes/PatofizyolojiVisual";
import { YildizVakasiVisual } from "../scenes/YildizVakasiVisual";
import { AlgoritmaVisual } from "../scenes/AlgoritmaVisual";
import { NARRATIVE_ORDER } from "../data/nodeLayout";

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

/** Per-katman camera direction so transitions feel like a film cut */
type CameraMove =
  | "zoom-in" /* straight forward dolly */
  | "oblique" /* tilt down + forward */
  | "pan-right"
  | "pan-left"
  | "spin"
  | "pullback"
  | "fly-up"
  | "fly-down"
  | "warp";

const CAMERA: Record<string, CameraMove> = {
  "1": "zoom-in",
  "2": "warp",
  "3": "oblique",
  "4": "pan-right",
  "5": "fly-up",
  "6": "pan-left",
  "7": "oblique",
  "8": "spin",
  "9": "pan-right",
  "10": "warp",
  "11": "fly-down",
  "12.1": "zoom-in",
  "12.2": "pan-right",
  "12.3": "oblique",
  "12.4": "pan-left",
  "12.5": "spin",
  "12.6": "pan-right",
  "12.7": "fly-up",
  "12.8": "pan-left",
  "12.9": "warp",
  "13": "pullback",
};

const SUPERSCRIPTS = "¹²³⁴⁵⁶⁷⁸⁹⁰";

function renderParagraph(p: string): React.ReactNode {
  const parts: React.ReactNode[] = [];
  let buf = "";
  for (let i = 0; i < p.length; i++) {
    const ch = p[i];
    if (SUPERSCRIPTS.includes(ch)) {
      if (buf) {
        parts.push(buf);
        buf = "";
      }
      let s = ch;
      while (i + 1 < p.length && SUPERSCRIPTS.includes(p[i + 1])) {
        i++;
        s += p[i];
      }
      parts.push(<sup key={`s-${i}`}>{s}</sup>);
    } else {
      buf += ch;
    }
  }
  if (buf) parts.push(buf);
  return parts;
}

function classify(p: string): string {
  const t = p.trim();
  if (t.length < 60 && !t.endsWith(":")) return "short";
  if (t.startsWith("—")) return "dialog";
  return "";
}

type Props = {
  story: Story;
};

/**
 * Tek sürekli bir kamera yolculuğu. Sticky viewport içinde 21 sahne
 * scroll'la kademeli olarak doğar, çerçeveye girer ve sonraki sahneye
 * doğru "geçer" (oblik tilt, dolly zoom, pan, spin, warp, pullback).
 */
export function CinematicJourney({ story }: Props) {
  const sectionsById: Record<string, Section> = {};
  for (const s of story.sections) sectionsById[s.id] = s;

  const ref = useRef<HTMLDivElement | null>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end end"],
  });

  // Per-katman scroll range
  const ranges = NARRATIVE_ORDER.reduce<Record<string, [number, number]>>(
    (acc, id, i) => {
      const segment = 1 / NARRATIVE_ORDER.length;
      acc[id] = [i * segment, (i + 1) * segment];
      return acc;
    },
    {},
  );

  return (
    <div
      ref={ref}
      className="cj"
      style={{ height: `${NARRATIVE_ORDER.length * 140}vh` }}
    >
      <div className="cj__viewport">
        <div className="cj__stage">
          {NARRATIVE_ORDER.map((id) => {
            const section = sectionsById[id];
            if (!section) return null;
            const Visual = SCENE_VISUALS[id];
            const range = ranges[id];
            const camera = CAMERA[id] ?? "zoom-in";
            return (
              <CinematicLayer
                key={id}
                id={id}
                range={range}
                progress={scrollYProgress}
                Visual={Visual}
                camera={camera}
              />
            );
          })}
        </div>

        <div className="cj__text-frame">
          {NARRATIVE_ORDER.map((id) => {
            const section = sectionsById[id];
            if (!section) return null;
            return (
              <CinematicText
                key={id}
                section={section}
                range={ranges[id]}
                progress={scrollYProgress}
              />
            );
          })}
        </div>

        <SceneIndicator progress={scrollYProgress} ranges={ranges} />
      </div>
    </div>
  );
}

/* ---------------- Layer ---------------- */

function CinematicLayer({
  id,
  range,
  progress,
  Visual,
  camera,
}: {
  id: string;
  range: [number, number];
  progress: MotionValue<number>;
  Visual?: React.ComponentType<{ progress: MotionValue<number> }>;
  camera: CameraMove;
}) {
  const [r0, r1] = range;
  const inEdge = r0 + (r1 - r0) * 0.18;
  const outEdge = r1 - (r1 - r0) * 0.18;

  const localProgress = useTransform(progress, [r0, r1], [0, 1]);

  // Core zoom + opacity envelope
  const scale = useTransform(
    progress,
    [r0, inEdge, outEdge, r1],
    [0.32, 1, 1, cameraOutScale(camera)],
  );
  const opacity = useTransform(
    progress,
    [r0, r0 + (inEdge - r0) * 0.55, outEdge + (r1 - outEdge) * 0.45, r1],
    [0, 1, 1, 0],
  );
  const blur = useTransform(
    progress,
    [r0, inEdge, outEdge, r1],
    ["18px", "0px", "0px", "14px"],
  );

  // Camera move – axis-specific transforms
  const rotateX = useTransform(progress, [r0, r1], cameraRotateX(camera));
  const rotateY = useTransform(progress, [r0, r1], cameraRotateY(camera));
  const rotateZ = useTransform(progress, [r0, r1], cameraRotateZ(camera));
  const x = useTransform(progress, [r0, r1], cameraX(camera));
  const y = useTransform(progress, [r0, r1], cameraY(camera));

  return (
    <motion.div
      className="cj__layer"
      data-id={id}
      data-camera={camera}
      style={{
        scale,
        opacity,
        filter: useTransform(blur, (v) => `blur(${v})`),
        rotateX,
        rotateY,
        rotateZ,
        x,
        y,
      }}
    >
      {Visual ? (
        <Visual progress={localProgress} />
      ) : (
        <AmbientVisual id={id} progress={localProgress} />
      )}
    </motion.div>
  );
}

function cameraOutScale(c: CameraMove): number {
  switch (c) {
    case "pullback":
      return 0.18;
    case "warp":
      return 14;
    case "fly-up":
    case "fly-down":
      return 9;
    case "spin":
      return 8;
    default:
      return 7;
  }
}

function cameraRotateX(c: CameraMove): [number, number] {
  switch (c) {
    case "oblique":
      return [-18, 6];
    case "fly-up":
      return [10, -22];
    case "fly-down":
      return [-12, 24];
    default:
      return [0, 0];
  }
}

function cameraRotateY(c: CameraMove): [number, number] {
  switch (c) {
    case "pan-right":
      return [-26, 18];
    case "pan-left":
      return [26, -18];
    case "oblique":
      return [-12, 4];
    default:
      return [0, 0];
  }
}

function cameraRotateZ(c: CameraMove): [number, number] {
  switch (c) {
    case "spin":
      return [-30, 30];
    case "warp":
      return [-8, 8];
    default:
      return [0, 0];
  }
}

function cameraX(c: CameraMove): [string, string] {
  switch (c) {
    case "pan-right":
      return ["-22%", "22%"];
    case "pan-left":
      return ["22%", "-22%"];
    default:
      return ["0%", "0%"];
  }
}

function cameraY(c: CameraMove): [string, string] {
  switch (c) {
    case "fly-up":
      return ["18%", "-18%"];
    case "fly-down":
      return ["-18%", "18%"];
    default:
      return ["0%", "0%"];
  }
}

/* ---------------- Text overlay ---------------- */

function CinematicText({
  section,
  range,
  progress,
}: {
  section: Section;
  range: [number, number];
  progress: MotionValue<number>;
}) {
  const [r0, r1] = range;
  const theme = layerTheme(section.id);
  const span = r1 - r0;

  // Opacity envelope: fade in, hold, fade out
  const opacity = useTransform(
    progress,
    [r0, r0 + span * 0.08, r1 - span * 0.12, r1],
    [0, 1, 1, 0],
  );

  // Translate so text drifts upward through the viewport for the duration
  const y = useTransform(progress, [r0, r1], ["55vh", "-65vh"]);

  // Title scales up subtly as it enters
  const titleScale = useTransform(
    progress,
    [r0, r0 + span * 0.15],
    [0.85, 1],
  );

  return (
    <motion.div
      className="cj__text"
      style={{
        opacity,
        y,
        ["--accent-current" as never]: theme.accent,
      }}
    >
      <div className="cj__text-head">
        <div className="cj__text-id" style={{ color: theme.accent }}>
          <span className="cj__text-glyph">{theme.glyph}</span>
          KATMAN {section.id} · {theme.label.toUpperCase()}
        </div>
        {theme.tagline && (
          <div className="cj__text-tagline">{theme.tagline}</div>
        )}
        <motion.h2
          className="cj__text-title"
          style={{ scale: titleScale, transformOrigin: "left center" }}
        >
          {section.title}
        </motion.h2>
      </div>

      <div className="cj__text-body">
        {section.paragraphs.map((p, i) => {
          const variant = classify(p);
          return (
            <p
              key={i}
              className={variant}
              style={variant === "short" ? { color: theme.accent } : undefined}
            >
              {renderParagraph(p)}
            </p>
          );
        })}
      </div>
    </motion.div>
  );
}

/* ---------------- Scene indicator ---------------- */

function SceneIndicator({
  progress,
  ranges,
}: {
  progress: MotionValue<number>;
  ranges: Record<string, [number, number]>;
}) {
  return (
    <div className="cj__indicator" aria-hidden="true">
      <div className="cj__indicator-line">
        <motion.div
          className="cj__indicator-fill"
          style={{ scaleY: progress, transformOrigin: "top center" }}
        />
      </div>
      <div className="cj__indicator-counts">
        {NARRATIVE_ORDER.map((id) => (
          <SceneDot
            key={id}
            id={id}
            progress={progress}
            range={ranges[id]}
          />
        ))}
      </div>
    </div>
  );
}

function SceneDot({
  id,
  progress,
  range,
}: {
  id: string;
  progress: MotionValue<number>;
  range: [number, number];
}) {
  const theme = layerTheme(id);
  const [r0, r1] = range;
  const opacity = useTransform(
    progress,
    [r0 - 0.005, r0, r1, r1 + 0.005],
    [0.25, 1, 1, 0.25],
  );
  return (
    <motion.span
      className="cj__indicator-dot"
      style={{ background: theme.accent, opacity }}
    />
  );
}
