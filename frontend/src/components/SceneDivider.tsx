import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { layerTheme } from "../layerThemes";

/**
 * Pin'lenmiş sahneler arası geçiş çubuğu. Aksan renginde dik bir
 * ışın kullanıcı içinden geçerken sol → sağ yatay bir bant çekiyor;
 * sonra söner. Sahne kesimi gibi hissedilen ince bir mola.
 */
export function SceneDivider({
  fromId,
  toId,
}: {
  fromId: string;
  toId: string;
}) {
  const ref = useRef<HTMLDivElement | null>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });
  const themeTo = layerTheme(toId);

  // Sweep line crosses left -> right
  const sweepX = useTransform(scrollYProgress, [0.2, 0.8], ["-110%", "110%"]);
  const sweepOpacity = useTransform(
    scrollYProgress,
    [0.15, 0.5, 0.85],
    [0, 1, 0],
  );

  // Number transition: from → to
  const fromOpacity = useTransform(
    scrollYProgress,
    [0.0, 0.35, 0.5],
    [0.6, 0.6, 0],
  );
  const toOpacity = useTransform(
    scrollYProgress,
    [0.5, 0.65, 0.9],
    [0, 0.85, 0.85],
  );

  return (
    <div ref={ref} className="divider" aria-hidden="true">
      <motion.div
        className="divider__sweep"
        style={{
          x: sweepX,
          opacity: sweepOpacity,
          background: `linear-gradient(90deg, transparent, ${themeTo.accent} 50%, transparent)`,
        }}
      />
      <div className="divider__nums">
        <motion.span className="divider__from" style={{ opacity: fromOpacity }}>
          KATMAN {fromId}
        </motion.span>
        <motion.span
          className="divider__to"
          style={{ opacity: toOpacity, color: themeTo.accent }}
        >
          KATMAN {toId} · {themeTo.label}
        </motion.span>
      </div>
    </div>
  );
}
