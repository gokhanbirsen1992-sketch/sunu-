import { useEffect, useState } from "react";
import {
  motion,
  useMotionValueEvent,
  useTransform,
  type MotionValue,
} from "framer-motion";

type Props = { progress: MotionValue<number> };

/**
 * KATMAN 5 — Embriyoloji
 *
 * "Yıldız'ın karaciğeri 26. günde başladı." Embriyodan hepatik
 * divertikül tomurcuklanır; 12. haftada safra üretilir.
 * Doğumda UGT1A1 aktivitesi %0.1'den postnatal haftalarda %100'e
 * sıçrar — fizyolojik yenidoğan sarılığının moleküler nedeni.
 */
export function EmbriyolojiVisual({ progress }: Props) {
  // Phases
  const day26Opacity = useTransform(progress, [0, 0.05, 0.35, 0.45], [0, 1, 1, 0.25]);
  const week6Opacity = useTransform(progress, [0.2, 0.3, 0.5, 0.6], [0, 1, 1, 0.3]);
  const week12Opacity = useTransform(progress, [0.4, 0.5, 0.62, 0.72], [0, 1, 1, 0.3]);

  // The liver bud grows
  const liverScale = useTransform(progress, [0.05, 0.7], [0.3, 1]);

  // UGT1A1 line chart progress
  const lineDraw = useTransform(progress, [0.55, 0.95], [0, 1]);
  const dotsOpacity = useTransform(progress, [0.7, 0.85], [0, 1]);

  // Bilirubin reading on Yıldız at the end
  const bili = useTransform(progress, [0.85, 1], [0, 28]);
  const [biliText, setBiliText] = useState("0");
  useMotionValueEvent(bili, "change", (v) => setBiliText(Math.round(v).toString()));
  useEffect(() => setBiliText(Math.round(bili.get()).toString()), [bili]);

  const labelOpacity = useTransform(progress, [0.83, 0.95], [0, 1]);

  return (
    <svg
      viewBox="-100 -100 200 200"
      className="visual-svg"
      preserveAspectRatio="xMidYMid meet"
      aria-hidden="true"
    >
      <defs>
        <radialGradient id="emb-glow">
          <stop offset="0%" stopColor="#f472b6" stopOpacity="0.5" />
          <stop offset="100%" stopColor="#f472b6" stopOpacity="0" />
        </radialGradient>
      </defs>

      {/* Embryo silhouette — simplified curl */}
      <g transform="translate(-25, -40)">
        <motion.path
          d="M 0 0 C 18 -8, 28 4, 24 22 C 22 36, 14 44, 0 44 C -10 44, -14 38, -12 28 C -10 18, -6 12, 0 0 Z"
          fill="rgba(244, 114, 182, 0.12)"
          stroke="#f472b6"
          strokeWidth={0.6}
          opacity={0.85}
        />
        {/* Day-26 hepatic diverticulum: tiny bud */}
        <motion.g style={{ opacity: day26Opacity }}>
          <circle cx={14} cy={20} r={3.2} fill="#f472b6" opacity={0.9} />
          <text
            x={26}
            y={22}
            fontFamily="ui-sans-serif, system-ui"
            fontSize={4.4}
            fill="#f472b6"
            opacity={0.85}
          >
            26. gün · hepatik divertikül
          </text>
        </motion.g>
      </g>

      {/* Week 6 — liver visible, growing */}
      <motion.g style={{ opacity: week6Opacity }}>
        <motion.path
          d="M -15 0 C -8 -14, 12 -12, 22 -2 C 28 8, 22 18, 8 18 C -6 16, -16 10, -15 0 Z"
          stroke={"#fb923c" as string}
          strokeWidth={0.7}
          fill="url(#emb-glow)"
          transform="translate(-25, -8)"
          style={{
            scale: liverScale,
            transformOrigin: "-25px -8px",
          }}
        />
        <text
          x={-50}
          y={20}
          fontFamily="ui-sans-serif, system-ui"
          fontSize={4.6}
          fill="#fb923c"
          opacity={0.8}
        >
          6. hafta · karaciğer şekilleniyor
        </text>
      </motion.g>

      {/* Week 12 - safra üretimi başlar */}
      <motion.g style={{ opacity: week12Opacity }}>
        <text
          x={-50}
          y={42}
          fontFamily="ui-sans-serif, system-ui"
          fontSize={4.6}
          fill="#f5b942"
          opacity={0.85}
        >
          12. hafta · safra üretimi
        </text>
        <motion.circle
          cx={-32}
          cy={5}
          r={6}
          fill="none"
          stroke="#f5b942"
          strokeWidth={0.5}
          strokeDasharray="2 2"
          opacity={0.75}
        />
        <motion.circle cx={-32} cy={5} r={2} fill="#f5b942" opacity={0.9} />
      </motion.g>

      {/* UGT1A1 enzyme activity chart — bottom panel */}
      <g transform="translate(0, 50)">
        {/* Axes */}
        <line x1={-78} y1={0} x2={88} y2={0} stroke="rgba(236,232,223,0.4)" strokeWidth={0.4} />
        <line x1={-78} y1={-32} x2={-78} y2={2} stroke="rgba(236,232,223,0.4)" strokeWidth={0.4} />
        <text
          x={-78}
          y={11}
          fontFamily="ui-sans-serif, system-ui"
          fontSize={3.6}
          fill="rgba(236,232,223,0.55)"
        >
          fetal
        </text>
        <text
          x={-30}
          y={11}
          fontFamily="ui-sans-serif, system-ui"
          fontSize={3.6}
          fill="rgba(236,232,223,0.55)"
        >
          doğum
        </text>
        <text
          x={70}
          y={11}
          fontFamily="ui-sans-serif, system-ui"
          fontSize={3.6}
          fill="rgba(236,232,223,0.55)"
          textAnchor="end"
        >
          erişkin
        </text>
        <text
          x={-86}
          y={-1}
          fontFamily="ui-sans-serif, system-ui"
          fontSize={3.6}
          fill="rgba(236,232,223,0.55)"
          textAnchor="end"
        >
          0%
        </text>
        <text
          x={-86}
          y={-30}
          fontFamily="ui-sans-serif, system-ui"
          fontSize={3.6}
          fill="rgba(236,232,223,0.55)"
          textAnchor="end"
        >
          100%
        </text>

        {/* UGT1A1 activity curve: flat near 0 fetal, sharp rise postnatal */}
        <motion.path
          d="M -78 -1 L -32 -2 C -16 -3, -20 -8, -8 -16 C 6 -24, 36 -30, 88 -32"
          fill="none"
          stroke="#c084fc"
          strokeWidth={0.9}
          style={{
            pathLength: lineDraw,
          }}
        />
        <motion.text
          x={45}
          y={-26}
          fontFamily="ui-sans-serif, system-ui"
          fontSize={4.4}
          fill="#c084fc"
          opacity={0.85}
          style={{ opacity: dotsOpacity }}
        >
          UGT1A1
        </motion.text>

        {/* Dots */}
        <motion.g style={{ opacity: dotsOpacity }} fill="#c084fc">
          <circle cx={-32} cy={-2} r={1.6} />
          <circle cx={-12} cy={-12} r={1.6} />
          <circle cx={20} cy={-26} r={1.6} />
        </motion.g>
      </g>

      {/* Yıldız outcome */}
      <motion.g style={{ opacity: labelOpacity }} transform="translate(50, -50)">
        <circle cx={0} cy={0} r={20} fill="url(#emb-glow)" />
        <circle cx={0} cy={0} r={11} fill={"#fde68a"} opacity={0.8} />
        <text
          x={0}
          y={3}
          textAnchor="middle"
          fontFamily="'Cormorant Garamond', serif"
          fontWeight={500}
          fontSize={11}
          fill="#fff"
        >
          {biliText}
        </text>
        <text
          x={0}
          y={32}
          textAnchor="middle"
          fontFamily="ui-sans-serif, system-ui"
          fontSize={3.8}
          letterSpacing={1.4}
          fill="#fde68a"
        >
          YILDIZ · BİLİRUBİN
        </text>
      </motion.g>
    </svg>
  );
}
