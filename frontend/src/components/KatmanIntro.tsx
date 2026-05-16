import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { layerTheme } from "../layerThemes";

type Props = {
  id: string;
};

/**
 * Scroll'a kilitli bir geçiş divider'ı. Her katman'dan önce 80vh
 * yüksekliğinde render edilir; kullanıcı içinden geçerken:
 *  - Aksan rengi yumuşak bir parlama doğar
 *  - Yatay bir ışın çizgisi soldan sağa süpürür
 *  - Devasa katman numarası + glyph + label aşağıdan yukarı yükselir,
 *    ekran ortasında büyür, sonra üstte küçülüp solar
 */
export function KatmanIntro({ id }: Props) {
  const ref = useRef<HTMLDivElement | null>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });
  const theme = layerTheme(id);

  const burstOpacity = useTransform(
    scrollYProgress,
    [0.15, 0.5, 0.85],
    [0, 1, 0],
  );
  const burstScale = useTransform(scrollYProgress, [0, 1], [0.6, 1.6]);

  const sweepX = useTransform(scrollYProgress, [0.35, 0.65], ["-110%", "110%"]);
  const sweepOpacity = useTransform(
    scrollYProgress,
    [0.3, 0.5, 0.7],
    [0, 1, 0],
  );

  const contentY = useTransform(
    scrollYProgress,
    [0, 0.45, 0.6, 1],
    [120, 0, 0, -120],
  );
  const contentOpacity = useTransform(
    scrollYProgress,
    [0.05, 0.3, 0.7, 0.95],
    [0, 1, 1, 0],
  );
  const numScale = useTransform(
    scrollYProgress,
    [0, 0.4, 0.6, 1],
    [0.55, 1, 1.05, 0.55],
  );

  return (
    <div ref={ref} className="katman-intro" aria-hidden="true">
      <motion.div
        className="katman-intro__burst"
        style={{
          opacity: burstOpacity,
          scale: burstScale,
          background: `radial-gradient(circle at center, ${theme.accent}33, transparent 60%)`,
        }}
      />
      <motion.div
        className="katman-intro__sweep"
        style={{
          x: sweepX,
          opacity: sweepOpacity,
          background: `linear-gradient(90deg, transparent, ${theme.accent}, transparent)`,
        }}
      />
      <motion.div
        className="katman-intro__content"
        style={{ y: contentY, opacity: contentOpacity }}
      >
        <div
          className="katman-intro__kicker"
          style={{ color: theme.accent }}
        >
          KATMAN {id}
        </div>
        <motion.div
          className="katman-intro__glyph"
          style={{ color: theme.accent, scale: numScale }}
        >
          {theme.glyph}
        </motion.div>
        <div
          className="katman-intro__label"
          style={{ color: theme.accent }}
        >
          {theme.label}
        </div>
        {theme.tagline && (
          <div className="katman-intro__tagline">{theme.tagline}</div>
        )}
      </motion.div>
    </div>
  );
}
