import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { layerTheme } from "../layerThemes";

type Props = {
  id: string;
};

/**
 * "Portal" transition between katmans.
 *
 * 100vh sticky'li bir bölge — kullanıcı içinden geçerken:
 * - Aksan renkli radyal perde aşağıdan yükselir, ekranı kaplar,
 *   sonra üstten süzülüp gider
 * - Tam orta noktada warp çizgileri dışa fırlar
 * - Dev katman glyph'i hafifçe dönerek görünür, geçişin tepesinde
 *   en büyük halini alır, sonra ileri zoom yaparak çıkar
 * - Açıkça hissedilen bir "sahne arası" — fade-in değil, perde.
 */
export function KatmanIntro({ id }: Props) {
  const ref = useRef<HTMLDivElement | null>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end end"],
  });
  const theme = layerTheme(id);

  // Curtain slides in from below, holds for a beat, slides off the top
  const curtainY = useTransform(
    scrollYProgress,
    [0, 0.32, 0.55, 0.9],
    ["100%", "0%", "0%", "-100%"],
  );

  // Glyph: starts small/rotated, peaks at center, zooms out as curtain leaves
  const glyphScale = useTransform(
    scrollYProgress,
    [0.25, 0.45, 0.55, 0.75],
    [0.4, 1, 1.05, 1.8],
  );
  const glyphRotate = useTransform(
    scrollYProgress,
    [0.25, 0.75],
    [-22, 22],
  );
  const glyphOpacity = useTransform(
    scrollYProgress,
    [0.28, 0.4, 0.62, 0.78],
    [0, 1, 1, 0],
  );

  // Number + label crawl up
  const labelY = useTransform(
    scrollYProgress,
    [0.3, 0.7],
    [30, -30],
  );
  const labelOpacity = useTransform(
    scrollYProgress,
    [0.32, 0.45, 0.6, 0.72],
    [0, 1, 1, 0],
  );

  // Warp streaks fire outward at peak
  const streakOpacity = useTransform(
    scrollYProgress,
    [0.4, 0.5, 0.65],
    [0, 0.85, 0],
  );
  const streakScale = useTransform(scrollYProgress, [0.4, 0.65], [0.4, 2.6]);

  // Quick flash at the curtain's apex
  const flashOpacity = useTransform(
    scrollYProgress,
    [0.48, 0.52, 0.56],
    [0, 1, 0],
  );

  return (
    <div ref={ref} className="katman-portal" aria-hidden="true">
      <div className="katman-portal__sticky">
        {/* Curtain — radial accent gradient slab */}
        <motion.div
          className="katman-portal__curtain"
          style={{
            y: curtainY,
            background: `radial-gradient(ellipse at center, ${theme.accent}ee 0%, ${theme.accent}cc 30%, ${theme.accent}55 70%, ${theme.accent}11 100%)`,
          }}
        />

        {/* Warp streaks radiating outward */}
        <motion.div
          className="katman-portal__streaks"
          style={{ opacity: streakOpacity, scale: streakScale }}
        >
          <svg
            viewBox="-100 -100 200 200"
            preserveAspectRatio="xMidYMid slice"
          >
            {Array.from({ length: 32 }).map((_, i) => {
              const angle = ((i * 360) / 32) * (Math.PI / 180);
              const r1 = 24;
              const r2 = 180;
              return (
                <line
                  key={i}
                  x1={Math.cos(angle) * r1}
                  y1={Math.sin(angle) * r1}
                  x2={Math.cos(angle) * r2}
                  y2={Math.sin(angle) * r2}
                  stroke="rgba(255, 255, 255, 0.85)"
                  strokeWidth={0.6}
                  strokeLinecap="round"
                />
              );
            })}
          </svg>
        </motion.div>

        {/* Peak flash */}
        <motion.div
          className="katman-portal__flash"
          style={{
            opacity: flashOpacity,
            background: `radial-gradient(circle, #fff 0%, ${theme.accent}00 60%)`,
          }}
        />

        {/* Giant glyph */}
        <motion.div
          className="katman-portal__glyph-wrap"
          style={{
            scale: glyphScale,
            rotate: glyphRotate,
            opacity: glyphOpacity,
          }}
        >
          <div className="katman-portal__glyph">{theme.glyph}</div>
        </motion.div>

        {/* Number + label, separately animated */}
        <motion.div
          className="katman-portal__label"
          style={{ y: labelY, opacity: labelOpacity }}
        >
          <div className="katman-portal__num">KATMAN {id}</div>
          <div className="katman-portal__name">{theme.label}</div>
          {theme.tagline && (
            <div className="katman-portal__tagline">{theme.tagline}</div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
