import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import type { Story } from "../types";
import { layerTheme } from "../layerThemes";
import {
  CONNECTIONS,
  NARRATIVE_ORDER,
  NODE_POSITIONS,
} from "../data/nodeLayout";

type Props = {
  story: Story;
  onSelect: (id: string) => void;
};

type Star = {
  cx: number;
  cy: number;
  r: number;
  o: number;
  d: number;
};

function seededStars(count: number, seed = 7): Star[] {
  let s = seed;
  const rand = () => {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
  return Array.from({ length: count }, () => ({
    cx: rand() * 100,
    cy: rand() * 100,
    r: rand() * 1.4 + 0.2,
    o: rand() * 0.55 + 0.15,
    d: rand() * 5 + 3,
  }));
}

export function Hub({ story, onSelect }: Props) {
  const [hovered, setHovered] = useState<string | null>(null);
  const stars = useMemo(() => seededStars(240), []);

  const sectionsById = useMemo(() => {
    const map: Record<string, (typeof story.sections)[number]> = {};
    for (const s of story.sections) map[s.id] = s;
    return map;
  }, [story.sections]);

  return (
    <div className="hub">
      {/* Background starfield */}
      <svg
        className="hub__stars"
        viewBox="0 0 100 100"
        preserveAspectRatio="xMidYMid slice"
        aria-hidden="true"
      >
        {stars.map((star, i) => (
          <circle
            key={i}
            className="hub__star"
            cx={star.cx}
            cy={star.cy}
            r={star.r * 0.12}
            style={{
              opacity: star.o,
              animation: `twinkle ${star.d}s ease-in-out ${star.d * 0.3}s infinite`,
              ["--o" as never]: star.o,
            }}
          />
        ))}
      </svg>

      {/* Constellation lines */}
      <svg
        className="hub__lines"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        aria-hidden="true"
      >
        {CONNECTIONS.map(([a, b], i) => {
          const pa = NODE_POSITIONS[a];
          const pb = NODE_POSITIONS[b];
          if (!pa || !pb) return null;
          const active = hovered === a || hovered === b;
          return (
            <line
              key={i}
              x1={pa.x}
              y1={pa.y}
              x2={pb.x}
              y2={pb.y}
              stroke={active ? "rgba(245, 185, 66, 0.5)" : "rgba(236, 232, 223, 0.08)"}
              strokeWidth={0.18}
              style={{ transition: "stroke 280ms ease" }}
            />
          );
        })}
      </svg>

      {/* Yıldız — center */}
      <motion.div
        className="hub__yildiz"
        initial={{ opacity: 0, scale: 0.6 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1.2, delay: 0.15, ease: [0.2, 0.7, 0.3, 1] }}
      >
        <div className="hub__yildiz-glow" />
        <div className="hub__yildiz-core" />
        <div className="hub__yildiz-text">
          <div className="hub__yildiz-kicker">21 katmanda bilirubin</div>
          <div className="hub__yildiz-title">{story.title}</div>
          <div className="hub__yildiz-stat">
            <span className="hub__yildiz-num">28</span>
            <span className="hub__yildiz-unit">mg/dL · bilirubin · 96. saat</span>
          </div>
          <div className="hub__yildiz-hint">
            ✦ Bir takımyıldızdaki herhangi bir yıldıza tıkla
          </div>
        </div>
      </motion.div>

      {/* Nodes */}
      {NARRATIVE_ORDER.map((id, i) => {
        const pos = NODE_POSITIONS[id];
        const section = sectionsById[id];
        if (!pos || !section) return null;
        const theme = layerTheme(id);
        const isHover = hovered === id;
        return (
          <motion.button
            key={id}
            className="hub__node"
            type="button"
            initial={{ opacity: 0, scale: 0.6 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{
              duration: 0.7,
              delay: 0.4 + i * 0.04,
              ease: [0.2, 0.7, 0.3, 1],
            }}
            style={{
              left: `${pos.x}%`,
              top: `${pos.y}%`,
              ["--node-accent" as never]: theme.accent,
            }}
            onMouseEnter={() => setHovered(id)}
            onMouseLeave={() => setHovered(null)}
            onFocus={() => setHovered(id)}
            onBlur={() => setHovered(null)}
            onClick={() => onSelect(id)}
            aria-label={`Katman ${id} — ${theme.label}: ${section.title}`}
          >
            <span className="hub__node-pulse" aria-hidden="true" />
            <span className="hub__node-dot" aria-hidden="true">
              <span className="hub__node-glyph">{theme.glyph}</span>
            </span>
            <span className="hub__node-label">
              <span className="hub__node-id">{id}</span>
              <span className="hub__node-name">{theme.label}</span>
              {isHover && theme.tagline && (
                <span className="hub__node-tagline">{theme.tagline}</span>
              )}
            </span>
          </motion.button>
        );
      })}
    </div>
  );
}
