import { useEffect, useRef } from "react";
import {
  AnimatePresence,
  motion,
  useScroll,
  type MotionValue,
} from "framer-motion";
import type { Section, Story } from "../types";
import { layerTheme } from "../layerThemes";
import { AmbientVisual } from "../scenes/AmbientVisual";
import { CosmosVisual } from "../scenes/CosmosVisual";
import { BilirubinVisual } from "../scenes/BilirubinVisual";
import { HepatocyteVisual } from "../scenes/HepatocyteVisual";
import { ClosureVisual } from "../scenes/ClosureVisual";
import { NARRATIVE_ORDER, NODE_POSITIONS } from "../data/nodeLayout";

const SCENE_VISUALS: Record<
  string,
  React.ComponentType<{ progress: MotionValue<number> }>
> = {
  "1": CosmosVisual,
  "2": BilirubinVisual,
  "3": HepatocyteVisual,
  "13": ClosureVisual,
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
  activeId: string | null;
  onClose: () => void;
  onNavigate: (id: string) => void;
};

export function KatmanModal({ story, activeId, onClose, onNavigate }: Props) {
  return (
    <AnimatePresence mode="wait">
      {activeId && (
        <KatmanModalContent
          key={activeId}
          story={story}
          activeId={activeId}
          onClose={onClose}
          onNavigate={onNavigate}
        />
      )}
    </AnimatePresence>
  );
}

function KatmanModalContent({
  story,
  activeId,
  onClose,
  onNavigate,
}: {
  story: Story;
  activeId: string;
  onClose: () => void;
  onNavigate: (id: string) => void;
}) {
  const section: Section | undefined = story.sections.find(
    (s) => s.id === activeId,
  );
  const theme = layerTheme(activeId);
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const { scrollYProgress } = useScroll({ container: scrollRef });

  // Reset scroll on katman change
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: 0, behavior: "auto" });
  }, [activeId]);

  // Keyboard navigation
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      const idx = NARRATIVE_ORDER.indexOf(activeId);
      if (e.key === "ArrowRight" && idx < NARRATIVE_ORDER.length - 1) {
        onNavigate(NARRATIVE_ORDER[idx + 1]);
      }
      if (e.key === "ArrowLeft" && idx > 0) {
        onNavigate(NARRATIVE_ORDER[idx - 1]);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [activeId, onClose, onNavigate]);

  if (!section) return null;

  const idx = NARRATIVE_ORDER.indexOf(activeId);
  const prevId = idx > 0 ? NARRATIVE_ORDER[idx - 1] : null;
  const nextId =
    idx < NARRATIVE_ORDER.length - 1 ? NARRATIVE_ORDER[idx + 1] : null;
  const Bespoke = SCENE_VISUALS[activeId];

  // Compute slide-in origin (where the node sits in the hub)
  const origin = NODE_POSITIONS[activeId] ?? { x: 50, y: 50 };
  const originStyle = {
    transformOrigin: `${origin.x}% ${origin.y}%`,
  } as const;

  return (
    <motion.div
      className="modal"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.35, ease: [0.2, 0.7, 0.3, 1] }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      role="dialog"
      aria-modal="true"
      aria-label={`Katman ${activeId} — ${theme.label}`}
    >
      <motion.div
        className="modal__shell"
        style={{
          ["--accent-current" as never]: theme.accent,
          ...originStyle,
        }}
        initial={{ scale: 0.08, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.08, opacity: 0 }}
        transition={{
          duration: 0.55,
          ease: [0.2, 0.7, 0.3, 1],
        }}
      >
        <header className="modal__head">
          <button
            type="button"
            className="modal__back"
            onClick={onClose}
            aria-label="Haritaya dön"
          >
            <span aria-hidden="true">←</span> Harita
          </button>
          <div className="modal__head-mid">
            <div
              className="modal__head-id"
              style={{ color: theme.accent }}
            >
              <span className="modal__head-glyph">{theme.glyph}</span>
              KATMAN {activeId}
            </div>
            <div className="modal__head-label">{theme.label}</div>
          </div>
          <div className="modal__head-right">
            <button
              type="button"
              className="modal__nav-btn"
              onClick={() => prevId && onNavigate(prevId)}
              disabled={!prevId}
              aria-label="Önceki katman"
            >
              ←
            </button>
            <span className="modal__nav-count">
              {idx + 1} / {NARRATIVE_ORDER.length}
            </span>
            <button
              type="button"
              className="modal__nav-btn"
              onClick={() => nextId && onNavigate(nextId)}
              disabled={!nextId}
              aria-label="Sonraki katman"
            >
              →
            </button>
          </div>
        </header>

        <div className="modal__body">
          <div className="modal__visual">
            <div className="modal__visual-inner">
              {Bespoke ? (
                <Bespoke progress={scrollYProgress} />
              ) : (
                <AmbientVisual id={activeId} progress={scrollYProgress} />
              )}
            </div>
            <div
              className="modal__visual-bar"
              aria-hidden="true"
              style={{ background: theme.accent }}
            />
          </div>

          <div className="modal__scroll" ref={scrollRef}>
            <div className="modal__text">
              <div className="modal__text-head">
                {theme.tagline && (
                  <div className="modal__tagline">{theme.tagline}</div>
                )}
                <h2 className="modal__title">{section.title}</h2>
              </div>

              <div className="modal__paragraphs">
                {section.paragraphs.map((p, i) => {
                  const variant = classify(p);
                  return (
                    <motion.p
                      key={i}
                      className={variant}
                      initial={{ opacity: 0, y: 14 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{
                        duration: 0.5,
                        delay: 0.45 + Math.min(i * 0.025, 0.4),
                        ease: [0.2, 0.7, 0.3, 1],
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

              {nextId && (
                <button
                  type="button"
                  className="modal__next"
                  onClick={() => onNavigate(nextId)}
                  style={{
                    ["--accent-current" as never]: layerTheme(nextId).accent,
                  }}
                >
                  <span className="modal__next-arrow">→</span>
                  <span>
                    <span className="modal__next-label">Sonraki katman</span>
                    <span className="modal__next-title">
                      KATMAN {nextId} · {layerTheme(nextId).label}
                    </span>
                  </span>
                </button>
              )}
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
