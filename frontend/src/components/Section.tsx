import { motion } from "framer-motion";
import type { Section as SectionData } from "../types";
import { layerTheme } from "../layerThemes";

type Props = {
  section: SectionData;
  index: number;
};

const SUPERSCRIPTS = "¹²³⁴⁵⁶⁷⁸⁹⁰";

function renderParagraph(p: string): React.ReactNode {
  // Wrap trailing superscript citation digits in <sup>
  const parts: React.ReactNode[] = [];
  let buf = "";
  for (let i = 0; i < p.length; i++) {
    const ch = p[i];
    if (SUPERSCRIPTS.includes(ch)) {
      if (buf) {
        parts.push(buf);
        buf = "";
      }
      // Collect consecutive superscripts
      let s = ch;
      while (i + 1 < p.length && SUPERSCRIPTS.includes(p[i + 1])) {
        i++;
        s += p[i];
      }
      parts.push(
        <sup key={`s-${i}`}>{s}</sup>
      );
    } else {
      buf += ch;
    }
  }
  if (buf) parts.push(buf);
  return parts;
}

function classifyParagraph(p: string): string {
  const trimmed = p.trim();
  // Single-sentence beats — short, punchy, often standalone lines
  if (trimmed.length < 60 && !trimmed.endsWith(":")) return "short";
  // Quoted dialog (very rough heuristic: leading quote)
  if (trimmed.startsWith("—") || trimmed.startsWith("«") || trimmed.startsWith("\"")) {
    return "dialog";
  }
  return "";
}

export function SectionView({ section, index }: Props) {
  const theme = layerTheme(section.id);
  return (
    <motion.section
      className="section"
      id={`katman-${section.id}`}
      data-index={index}
      style={{ ["--accent-current" as never]: theme.accent }}
    >
      <motion.header
        className="section__header"
        initial={{ opacity: 0, y: 28 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.4 }}
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

      <div className="section__body">
        {section.paragraphs.map((p, i) => {
          const variant = classifyParagraph(p);
          return (
            <motion.p
              key={i}
              className={variant}
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.2, margin: "0px 0px -10% 0px" }}
              transition={{
                duration: 0.7,
                delay: Math.min(i * 0.04, 0.3),
                ease: [0.2, 0.65, 0.3, 1],
              }}
              style={
                variant === "short"
                  ? { color: theme.accent }
                  : undefined
              }
            >
              {renderParagraph(p)}
            </motion.p>
          );
        })}
      </div>
    </motion.section>
  );
}
