import { motion, useTransform, type MotionValue } from "framer-motion";

type Props = { progress: MotionValue<number> };

/**
 * KATMAN 1 — Kozmoloji
 *
 * Big Bang → hidrojen scatter → karbon emergence (Hoyle 7.65 MeV) →
 * süpernova → demir → Yıldız doğar.
 */
export function CosmosVisual({ progress }: Props) {
  const bangScale = useTransform(progress, [0, 0.06, 0.18], [0, 3, 0.4]);
  const bangOpacity = useTransform(progress, [0, 0.04, 0.18], [0, 1, 0]);

  const hOpacity = useTransform(
    progress,
    [0.12, 0.22, 0.45, 0.55],
    [0, 1, 1, 0.2],
  );

  const cOpacity = useTransform(
    progress,
    [0.28, 0.4, 0.62, 0.72],
    [0, 1, 1, 0.25],
  );
  const cScale = useTransform(progress, [0.28, 0.4], [0.4, 1]);

  const novaFlashOpacity = useTransform(
    progress,
    [0.55, 0.6, 0.7],
    [0, 1, 0],
  );
  const novaFlashScale = useTransform(progress, [0.55, 0.7], [0.3, 4]);

  const feOpacity = useTransform(
    progress,
    [0.6, 0.72, 0.88],
    [0, 1, 0.45],
  );
  const feScale = useTransform(progress, [0.6, 0.72], [0.4, 1]);

  const yıldızOpacity = useTransform(progress, [0.78, 0.95], [0, 1]);
  const yıldızScale = useTransform(progress, [0.78, 1], [0.2, 1]);

  return (
    <svg
      viewBox="-100 -100 200 200"
      className="visual-svg"
      preserveAspectRatio="xMidYMid meet"
      aria-hidden="true"
    >
      <defs>
        <radialGradient id="bang">
          <stop offset="0%" stopColor="#fff" stopOpacity="1" />
          <stop offset="40%" stopColor="#a78bfa" stopOpacity="0.8" />
          <stop offset="100%" stopColor="#a78bfa" stopOpacity="0" />
        </radialGradient>
        <radialGradient id="nova">
          <stop offset="0%" stopColor="#fff" stopOpacity="1" />
          <stop offset="30%" stopColor="#fb923c" stopOpacity="0.7" />
          <stop offset="100%" stopColor="#fb923c" stopOpacity="0" />
        </radialGradient>
        <radialGradient id="yıldız">
          <stop offset="0%" stopColor="#fff7e0" />
          <stop offset="35%" stopColor="#f5b942" />
          <stop offset="100%" stopColor="#f5b942" stopOpacity="0" />
        </radialGradient>
      </defs>

      <motion.circle
        cx={0}
        cy={0}
        r={14}
        fill="url(#bang)"
        style={{ scale: bangScale, opacity: bangOpacity, transformOrigin: "center" }}
      />

      {/* Hydrogen scatter — drifting blue dots */}
      <motion.g style={{ opacity: hOpacity }}>
        {Array.from({ length: 60 }).map((_, i) => {
          const seed = i * 0.6180339887;
          const angle = (i * 137.5 * Math.PI) / 180;
          const r = 25 + (seed * 60) % 55;
          const x = Math.cos(angle) * r;
          const y = Math.sin(angle) * r;
          return (
            <circle
              key={i}
              cx={x}
              cy={y}
              r={0.55}
              fill="#7dd3fc"
              opacity={0.4 + ((seed * 7) % 1) * 0.6}
            />
          );
        })}
      </motion.g>

      {/* Carbon emerges — 3 He → 1 C (Hoyle) */}
      <motion.g
        style={{ opacity: cOpacity, scale: cScale, transformOrigin: "center" }}
      >
        {[
          { x: -45, y: -30 },
          { x: 50, y: -28 },
          { x: 0, y: 38 },
        ].map((p, i) => (
          <g key={i} transform={`translate(${p.x},${p.y})`}>
            <circle
              r={8}
              fill="rgba(167, 139, 250, 0.18)"
              stroke="#a78bfa"
              strokeWidth={0.6}
            />
            <text
              y={2.4}
              textAnchor="middle"
              fontSize={6.5}
              fontFamily="ui-sans-serif, system-ui"
              fontWeight={600}
              fill="#a78bfa"
            >
              C
            </text>
          </g>
        ))}
      </motion.g>

      {/* Supernova flash */}
      <motion.circle
        cx={0}
        cy={0}
        r={20}
        fill="url(#nova)"
        style={{
          opacity: novaFlashOpacity,
          scale: novaFlashScale,
          transformOrigin: "center",
        }}
      />

      {/* Iron — post-supernova */}
      <motion.g
        style={{ opacity: feOpacity, scale: feScale, transformOrigin: "center" }}
      >
        {[
          { x: -32, y: 18 },
          { x: 36, y: 20 },
          { x: -8, y: -52 },
        ].map((p, i) => (
          <g key={i} transform={`translate(${p.x},${p.y})`}>
            <circle
              r={7.5}
              fill="rgba(251, 146, 60, 0.18)"
              stroke="#fb923c"
              strokeWidth={0.6}
            />
            <text
              y={2.2}
              textAnchor="middle"
              fontSize={5.8}
              fontFamily="ui-sans-serif, system-ui"
              fontWeight={600}
              fill="#fb923c"
            >
              Fe
            </text>
          </g>
        ))}
      </motion.g>

      {/* Yıldız — bütün atomlar bir bebekte buluşur */}
      <motion.g
        style={{
          opacity: yıldızOpacity,
          scale: yıldızScale,
          transformOrigin: "center",
        }}
      >
        <circle cx={0} cy={0} r={42} fill="url(#yıldız)" />
        <circle cx={0} cy={0} r={16} fill="#fef9c3" opacity={0.85} />
        <text
          x={0}
          y={62}
          textAnchor="middle"
          fontSize={7}
          fontFamily="'Cormorant Garamond', serif"
          fontStyle="italic"
          fill="#fef3c7"
        >
          Yıldız
        </text>
      </motion.g>
    </svg>
  );
}
