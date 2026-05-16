import { useEffect, useState } from "react";
import { motion, useScroll, useSpring } from "framer-motion";
import { layerTheme } from "../layerThemes";
import { NARRATIVE_ORDER } from "../data/nodeLayout";

/**
 * Sağ kenarda dikey bir progress ray'i. Toplam scroll'u gösterir,
 * her katmanın yerini işaret eder, aktif olanı vurgular.
 */
export function ProgressRail() {
  const { scrollYProgress } = useScroll();
  const scaleY = useSpring(scrollYProgress, {
    stiffness: 120,
    damping: 28,
  });
  const [active, setActive] = useState<string>(NARRATIVE_ORDER[0]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) {
            const id = (e.target as HTMLElement).dataset.id;
            if (id) setActive(id);
          }
        }
      },
      { rootMargin: "-40% 0px -55% 0px", threshold: 0 },
    );
    document
      .querySelectorAll<HTMLElement>(".ss[data-id]")
      .forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  const scrollTo = (id: string) => {
    const el = document.querySelector<HTMLElement>(`.ss[data-id="${id}"]`);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <aside className="rail" aria-label="Katman ilerlemesi">
      <div className="rail__bar">
        <motion.div className="rail__fill" style={{ scaleY }} />
      </div>
      <div className="rail__ticks">
        {NARRATIVE_ORDER.map((id) => {
          const theme = layerTheme(id);
          const isActive = active === id;
          return (
            <button
              key={id}
              type="button"
              className="rail__tick"
              data-active={isActive}
              onClick={() => scrollTo(id)}
              style={{ ["--tick-accent" as never]: theme.accent }}
              aria-label={`Katman ${id} — ${theme.label}`}
            >
              <span className="rail__tick-dot" />
              <span className="rail__tick-label">
                <span className="rail__tick-id">{id}</span>
                <span className="rail__tick-name">{theme.label}</span>
              </span>
            </button>
          );
        })}
      </div>
    </aside>
  );
}
