import { useEffect, useState } from "react";
import {
  motion,
  useMotionValueEvent,
  useTransform,
  type MotionValue,
} from "framer-motion";

type Props = { progress: MotionValue<number> };

/**
 * KATMAN 11 — Patofizyoloji
 *
 * Kramer zonları: bilirubin baştan ayağa yayılır. Yıldız 96. saatte
 * Kramer 5 (palmer/plantar). Fototerapi ışığı altında 4 mg/dL'lik
 * sınırlı düşüş — enzim sıfır olduğu için ışık tek başına yetmiyor.
 */
export function PatofizyolojiVisual({ progress }: Props) {
  // Zones light up sequentially
  const z1 = useTransform(progress, [0.0, 0.08, 0.95], [0, 1, 1]);
  const z2 = useTransform(progress, [0.1, 0.2, 0.95], [0, 1, 1]);
  const z3 = useTransform(progress, [0.2, 0.32, 0.95], [0, 1, 1]);
  const z4 = useTransform(progress, [0.32, 0.45, 0.95], [0, 1, 1]);
  const z5 = useTransform(progress, [0.45, 0.6, 0.95], [0, 1, 1]);

  // Phototherapy beam fires in late
  const beamOpacity = useTransform(progress, [0.65, 0.8], [0, 0.7]);

  // Bilirubin level ticker: 28 → 24 (small drop under phototherapy)
  const bili = useTransform(progress, [0.0, 0.6, 1], [28, 28, 24]);
  const [biliText, setBiliText] = useState("28");
  useMotionValueEvent(bili, "change", (v) =>
    setBiliText(v.toFixed(0)),
  );
  useEffect(() => setBiliText(Math.round(bili.get()).toString()), [bili]);

  const labelOpacity = useTransform(progress, [0.05, 0.15], [0, 1]);

  return (
    <svg
      viewBox="-100 -100 200 200"
      className="visual-svg"
      preserveAspectRatio="xMidYMid meet"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="z1g">
          <stop offset="0%" stopColor="#fef3c7" />
          <stop offset="100%" stopColor="#fbbf24" />
        </linearGradient>
        <linearGradient id="z5g">
          <stop offset="0%" stopColor="#fb923c" />
          <stop offset="100%" stopColor="#dc2626" />
        </linearGradient>
        <linearGradient id="phototherapy-beam" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#60a5fa" stopOpacity="0" />
          <stop offset="100%" stopColor="#60a5fa" stopOpacity="0.55" />
        </linearGradient>
      </defs>

      {/* Phototherapy beam from top */}
      <motion.rect
        x={-50}
        y={-100}
        width={100}
        height={50}
        fill="url(#phototherapy-beam)"
        style={{ opacity: beamOpacity }}
      />

      {/* Baby silhouette — simplified head + body shape, vertical orientation */}
      <g transform="translate(0, -10)">
        {/* Head */}
        <motion.circle
          cx={0}
          cy={-50}
          r={18}
          fill="url(#z1g)"
          stroke="rgba(245,185,66,0.6)"
          strokeWidth={0.5}
          style={{ opacity: z1 }}
        />

        {/* Trunk (Zone 2) */}
        <motion.path
          d="M -16 -35 C -22 -25, -22 0, -16 14 L 16 14 C 22 0, 22 -25, 16 -35 Z"
          fill="#fbbf24"
          stroke="rgba(245,185,66,0.5)"
          strokeWidth={0.5}
          style={{ opacity: z2 }}
        />

        {/* Lower trunk / abdomen (Zone 3) */}
        <motion.path
          d="M -14 14 C -16 24, -16 36, -14 44 L 14 44 C 16 36, 16 24, 14 14 Z"
          fill="#f97316"
          stroke="rgba(249,115,22,0.5)"
          strokeWidth={0.5}
          style={{ opacity: z3 }}
        />

        {/* Limbs — arms (Zone 4 part 1) */}
        <motion.path
          d="M -16 -28 C -28 -20, -38 0, -42 20 C -44 26, -42 30, -38 28 C -34 26, -28 16, -20 0 Z"
          fill="#ea580c"
          stroke="rgba(234,88,12,0.5)"
          strokeWidth={0.5}
          style={{ opacity: z4 }}
        />
        <motion.path
          d="M 16 -28 C 28 -20, 38 0, 42 20 C 44 26, 42 30, 38 28 C 34 26, 28 16, 20 0 Z"
          fill="#ea580c"
          stroke="rgba(234,88,12,0.5)"
          strokeWidth={0.5}
          style={{ opacity: z4 }}
        />

        {/* Legs / lower extremities */}
        <motion.path
          d="M -14 44 L -16 64 C -18 70, -16 74, -10 74 L -6 74 L -6 44 Z"
          fill="#ea580c"
          style={{ opacity: z4 }}
        />
        <motion.path
          d="M 6 44 L 6 74 L 10 74 C 16 74, 18 70, 16 64 L 14 44 Z"
          fill="#ea580c"
          style={{ opacity: z4 }}
        />

        {/* Palms / soles (Zone 5) */}
        <motion.ellipse
          cx={-40}
          cy={29}
          rx={5}
          ry={3.5}
          fill="url(#z5g)"
          style={{ opacity: z5 }}
        />
        <motion.ellipse
          cx={40}
          cy={29}
          rx={5}
          ry={3.5}
          fill="url(#z5g)"
          style={{ opacity: z5 }}
        />
        <motion.ellipse
          cx={-8}
          cy={76}
          rx={5}
          ry={3.5}
          fill="url(#z5g)"
          style={{ opacity: z5 }}
        />
        <motion.ellipse
          cx={8}
          cy={76}
          rx={5}
          ry={3.5}
          fill="url(#z5g)"
          style={{ opacity: z5 }}
        />
      </g>

      {/* Kramer zone labels on the right */}
      <motion.g style={{ opacity: labelOpacity }}>
        <g transform="translate(58, -68)">
          <motion.text
            fontFamily="ui-sans-serif, system-ui"
            fontSize={4.4}
            fill="#fbbf24"
            style={{ opacity: z1 }}
          >
            Kramer 1 · yüz/skleral
          </motion.text>
        </g>
        <g transform="translate(58, -50)">
          <motion.text
            fontFamily="ui-sans-serif, system-ui"
            fontSize={4.4}
            fill="#fbbf24"
            style={{ opacity: z2 }}
          >
            Kramer 2 · göğüs
          </motion.text>
        </g>
        <g transform="translate(58, -32)">
          <motion.text
            fontFamily="ui-sans-serif, system-ui"
            fontSize={4.4}
            fill="#f97316"
            style={{ opacity: z3 }}
          >
            Kramer 3 · karın
          </motion.text>
        </g>
        <g transform="translate(58, -14)">
          <motion.text
            fontFamily="ui-sans-serif, system-ui"
            fontSize={4.4}
            fill="#ea580c"
            style={{ opacity: z4 }}
          >
            Kramer 4 · ekstremite
          </motion.text>
        </g>
        <g transform="translate(58, 4)">
          <motion.text
            fontFamily="ui-sans-serif, system-ui"
            fontSize={4.4}
            fontWeight={600}
            fill="#dc2626"
            style={{ opacity: z5 }}
          >
            Kramer 5 · palmer/plantar
          </motion.text>
          <motion.text
            x={0}
            y={6}
            fontFamily="ui-sans-serif, system-ui"
            fontStyle="italic"
            fontSize={3.6}
            fill="#fca5a5"
            style={{ opacity: z5 }}
          >
            Yıldız burada
          </motion.text>
        </g>
      </motion.g>

      {/* Bilirubin level top-left */}
      <g transform="translate(-78, -85)">
        <text
          fontFamily="ui-sans-serif, system-ui"
          fontSize={3.6}
          letterSpacing={1.4}
          fill="rgba(236,232,223,0.55)"
        >
          BİLİRUBİN mg/dL
        </text>
        <motion.text
          y={16}
          fontFamily="'Cormorant Garamond', serif"
          fontWeight={500}
          fontSize={20}
          fill="#fef3c7"
        >
          {biliText}
        </motion.text>
      </g>
    </svg>
  );
}
