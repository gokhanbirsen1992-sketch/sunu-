import { useRef } from "react";
import {
  motion,
  useScroll,
  useTransform,
  type MotionValue,
} from "framer-motion";
import type { Section, Story } from "../types";
import { layerTheme } from "../layerThemes";
import { NARRATIVE_ORDER } from "../data/nodeLayout";

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

type Props = { story: Story };

/**
 * 3D Stage'in üstünde kayan metin. Tüm scroll'u kaplayan tek konteyner,
 * içinde her katmanın metni kendi range'inde fade-in/out + drift yapar.
 */
export function TextOverlay({ story }: Props) {
  const sectionsById: Record<string, Section> = {};
  for (const s of story.sections) sectionsById[s.id] = s;

  const ref = useRef<HTMLDivElement | null>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end end"],
  });

  const ranges = NARRATIVE_ORDER.reduce<Record<string, [number, number]>>(
    (acc, id, i) => {
      const seg = 1 / NARRATIVE_ORDER.length;
      acc[id] = [i * seg, (i + 1) * seg];
      return acc;
    },
    {},
  );

  return (
    <div
      ref={ref}
      className="overlay"
      style={{ height: `${NARRATIVE_ORDER.length * 160}vh` }}
    >
      <div className="overlay__viewport">
        {NARRATIVE_ORDER.map((id, i) => {
          const section = sectionsById[id];
          if (!section) return null;
          return (
            <KatmanText
              key={id}
              section={section}
              range={ranges[id]}
              progress={scrollYProgress}
              isFirst={i === 0}
              isLast={i === NARRATIVE_ORDER.length - 1}
            />
          );
        })}

        <ProgressIndicator progress={scrollYProgress} ranges={ranges} />
      </div>
    </div>
  );
}

function KatmanText({
  section,
  range,
  progress,
  isFirst,
  isLast,
}: {
  section: Section;
  range: [number, number];
  progress: MotionValue<number>;
  isFirst: boolean;
  isLast: boolean;
}) {
  const [r0, r1] = range;
  const theme = layerTheme(section.id);
  const span = r1 - r0;

  // First katman: visible from scroll=0. Last katman: stays at end. Others: fade in/out.
  const opacity = useTransform(
    progress,
    isFirst
      ? [r0, r0 + span * 0.05, r1 - span * 0.18, r1]
      : isLast
        ? [r0, r0 + span * 0.15, r1, r1 + 0.001]
        : [r0, r0 + span * 0.12, r1 - span * 0.18, r1],
    isFirst ? [1, 1, 1, 0] : isLast ? [0, 1, 1, 1] : [0, 1, 1, 0],
  );
  // Subtle vertical drift instead of full-screen sweep
  const y = useTransform(progress, [r0, r1], ["8vh", "-8vh"]);
  const titleScale = useTransform(
    progress,
    [r0, r0 + span * 0.15],
    [0.92, 1],
  );

  return (
    <div
      className="overlay__text-wrap"
      style={{ ["--accent-current" as never]: theme.accent }}
    >
      <motion.div className="overlay__text" style={{ opacity, y }}>
        <div className="overlay__text-head">
          <div className="overlay__text-id" style={{ color: theme.accent }}>
            <span className="overlay__text-glyph">{theme.glyph}</span>
            KATMAN {section.id} · {theme.label.toUpperCase()}
          </div>
          {theme.tagline && (
            <div className="overlay__text-tagline">{theme.tagline}</div>
          )}
          <motion.h2
            className="overlay__text-title"
            style={{ scale: titleScale, transformOrigin: "left center" }}
          >
            {section.title}
          </motion.h2>
        </div>

        <div className="overlay__text-body">
          {section.paragraphs.map((p, i) => {
            const variant = classify(p);
            return (
              <p
                key={i}
                className={variant}
                style={
                  variant === "short" ? { color: theme.accent } : undefined
                }
              >
                {renderParagraph(p)}
              </p>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
}

function ProgressIndicator({
  progress,
  ranges,
}: {
  progress: MotionValue<number>;
  ranges: Record<string, [number, number]>;
}) {
  return (
    <div className="overlay__indicator" aria-hidden="true">
      <div className="overlay__indicator-line">
        <motion.div
          className="overlay__indicator-fill"
          style={{ scaleY: progress, transformOrigin: "top center" }}
        />
      </div>
      <div className="overlay__indicator-counts">
        {NARRATIVE_ORDER.map((id) => (
          <Dot
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

function Dot({
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
      className="overlay__indicator-dot"
      style={{ background: theme.accent, opacity }}
    />
  );
}
