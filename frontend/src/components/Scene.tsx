import { useRef } from "react";
import type { ReactNode } from "react";
import { motion, useScroll, type MotionValue } from "framer-motion";
import type { Section as SectionData } from "../types";
import { layerTheme } from "../layerThemes";

type Props = {
  section: SectionData;
  Visual: React.ComponentType<{ progress: MotionValue<number> }>;
  /** Optional intro element rendered above the text column (e.g. a pull quote). */
  intro?: ReactNode;
};

const SUPERSCRIPTS = "¹²³⁴⁵⁶⁷⁸⁹⁰";

function renderParagraph(p: string): ReactNode {
  const parts: ReactNode[] = [];
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

export function Scene({ section, Visual, intro }: Props) {
  const ref = useRef<HTMLElement | null>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end end"],
  });
  const theme = layerTheme(section.id);

  return (
    <section
      ref={ref}
      className="scene"
      id={`katman-${section.id}`}
      style={{
        ["--accent-current" as never]: theme.accent,
      }}
    >
      <div className="scene__visual">
        <div className="scene__visual-inner">
          <Visual progress={scrollYProgress} />
        </div>
      </div>

      <div className="scene__text">
        <motion.header
          className="section__header"
          initial={{ opacity: 0, y: 28 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.8, ease: [0.2, 0.65, 0.3, 1] }}
        >
          <div className="section__id" style={{ color: theme.accent }}>
            <span className="section__glyph">{theme.glyph}</span>
            Katman {section.id}
          </div>
          {theme.tagline && (
            <div className="section__tagline">{theme.tagline}</div>
          )}
          <div
            className="section__accent-rule"
            style={{ color: theme.accent }}
          />
          <h2 className="section__title">{section.title}</h2>
        </motion.header>

        {intro && <div className="scene__intro">{intro}</div>}

        <div className="section__body">
          {section.paragraphs.map((p, i) => {
            const variant = classify(p);
            return (
              <motion.p
                key={i}
                className={variant}
                initial={{ opacity: 0, y: 18 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.25 }}
                transition={{
                  duration: 0.6,
                  delay: Math.min(i * 0.03, 0.25),
                  ease: [0.2, 0.65, 0.3, 1],
                }}
                style={variant === "short" ? { color: theme.accent } : undefined}
              >
                {renderParagraph(p)}
              </motion.p>
            );
          })}
        </div>
      </div>
    </section>
  );
}
