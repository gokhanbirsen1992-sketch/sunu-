import { useEffect, useState } from "react";
import {
  motion,
  useMotionValueEvent,
  useTransform,
  type MotionValue,
} from "framer-motion";

type Props = { progress: MotionValue<number> };

/**
 * KATMAN 13 — Kapanış
 *
 * Yıldız fototerapi altında. Bilirubin metresi 28'den geriye doğru
 * yavaşça yumuşar, sarı parıltı azalır — ama hiç sıfır olmaz.
 */
export function ClosureVisual({ progress }: Props) {
  const bili = useTransform(progress, [0, 0.95, 1], [28, 14, 14]);
  const glowOpacity = useTransform(progress, [0, 1], [1, 0.45]);
  const glowScale = useTransform(progress, [0, 1], [1, 0.85]);
  const beamOpacity = useTransform(progress, [0, 0.1, 1], [0, 1, 1]);
  const numColor = useTransform(
    progress,
    [0, 0.5, 1],
    ["#fef3c7", "#f5b942", "#fde68a"],
  );

  const [display, setDisplay] = useState("28");
  useMotionValueEvent(bili, "change", (v) => {
    setDisplay(Math.round(v).toString());
  });
  useEffect(() => {
    setDisplay(Math.round(bili.get()).toString());
  }, [bili]);

  return (
    <svg
      viewBox="-100 -100 200 200"
      className="visual-svg"
      preserveAspectRatio="xMidYMid meet"
      aria-hidden="true"
    >
      <defs>
        <radialGradient id="kapanis-glow">
          <stop offset="0%" stopColor="#fff7e0" />
          <stop offset="35%" stopColor="#f5b942" />
          <stop offset="100%" stopColor="#f5b942" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="kapanis-beam" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#60a5fa" stopOpacity="0" />
          <stop offset="100%" stopColor="#60a5fa" stopOpacity="0.55" />
        </linearGradient>
      </defs>

      {/* Phototherapy beam */}
      <motion.rect
        x={-50}
        y={-110}
        width={100}
        height={70}
        fill="url(#kapanis-beam)"
        style={{ opacity: beamOpacity }}
      />

      {/* Yıldız glow */}
      <motion.circle
        cx={0}
        cy={6}
        r={56}
        fill="url(#kapanis-glow)"
        style={{
          opacity: glowOpacity,
          scale: glowScale,
          transformOrigin: "center",
        }}
      />

      {/* Inner core */}
      <motion.circle
        cx={0}
        cy={6}
        r={30}
        fill="#fff7e0"
        style={{ opacity: glowOpacity }}
        opacity={0.4}
      />

      {/* Bilirubin number */}
      <motion.text
        x={0}
        y={14}
        textAnchor="middle"
        fontFamily="'Cormorant Garamond', serif"
        fontWeight={500}
        fontSize={36}
        style={{ fill: numColor }}
      >
        {display}
      </motion.text>
      <text
        x={0}
        y={32}
        textAnchor="middle"
        fontFamily="ui-sans-serif, system-ui"
        fontSize={5}
        letterSpacing={2}
        fill="rgba(254, 243, 199, 0.7)"
      >
        BİLİRUBİN · mg/dL
      </text>

      {/* Caption */}
      <text
        x={0}
        y={70}
        textAnchor="middle"
        fontFamily="'Cormorant Garamond', serif"
        fontStyle="italic"
        fontSize={6.5}
        fill="rgba(254, 243, 199, 0.6)"
      >
        Yıldız hâlâ ışığın altında.
      </text>
    </svg>
  );
}
