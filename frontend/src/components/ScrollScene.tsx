import { useRef } from "react";
import {
  motion,
  useScroll,
  useTransform,
  type MotionValue,
} from "framer-motion";
import type { Section as SectionData } from "../types";
import { layerTheme } from "../layerThemes";

type Props = {
  section: SectionData;
  Visual: React.ComponentType<{ progress: MotionValue<number> }>;
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

/**
 * Scrollytelling scene: sticky bir görsel + onunla scroll'a kilitli
 * akan metin. Görsel `progress: 0..1` alır, scroll pozisyonuyla
 * sürekli yeniden çizilir (scrub).
 */
export function ScrollScene({ section, Visual }: Props) {
  const sectionRef = useRef<HTMLElement | null>(null);
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start start", "end end"],
  });
  const theme = layerTheme(section.id);

  // Section-level entry / exit framing
  const headerOpacity = useTransform(
    scrollYProgress,
    [0, 0.08, 0.9, 1],
    [0.4, 1, 1, 0.3],
  );

  // Subtle parallax for the sticky visual frame
  const visualScale = useTransform(scrollYProgress, [0, 0.5, 1], [0.95, 1, 0.95]);
  const visualGlow = useTransform(
    scrollYProgress,
    [0, 0.5, 1],
    [0.3, 1, 0.3],
  );

  return (
    <section
      ref={sectionRef}
      className="ss"
      data-id={section.id}
      style={{
        ["--accent-current" as never]: theme.accent,
      }}
    >
      {/* Sticky visual on the left — pinned for the whole section */}
      <div className="ss__sticky">
        <div className="ss__sticky-inner">
          <motion.div
            className="ss__visual-glow"
            style={{
              opacity: visualGlow,
              background: `radial-gradient(circle at center, ${theme.accent}33, transparent 70%)`,
            }}
          />
          <motion.div
            className="ss__visual"
            style={{ scale: visualScale }}
          >
            <Visual progress={scrollYProgress} />
          </motion.div>
          <motion.div
            className="ss__visual-meta"
            style={{ opacity: headerOpacity }}
          >
            <div
              className="ss__visual-id"
              style={{ color: theme.accent }}
            >
              <span className="ss__visual-glyph">{theme.glyph}</span>
              KATMAN {section.id}
            </div>
            {theme.tagline && (
              <div className="ss__visual-tagline">{theme.tagline}</div>
            )}
            <div className="ss__visual-label">{theme.label}</div>
          </motion.div>
        </div>
      </div>

      {/* Scrolling text column on the right */}
      <div className="ss__text">
        <motion.h2
          className="ss__title"
          initial={{ opacity: 0, y: 28 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        >
          {section.title}
        </motion.h2>

        <div className="ss__body">
          {section.paragraphs.map((p, i) => {
            const variant = classify(p);
            return (
              <motion.p
                key={i}
                className={variant}
                initial={{ opacity: 0, y: 22 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.4, margin: "0px 0px -20% 0px" }}
                transition={{
                  duration: 0.7,
                  delay: Math.min(i * 0.03, 0.3),
                  ease: [0.16, 1, 0.3, 1],
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
