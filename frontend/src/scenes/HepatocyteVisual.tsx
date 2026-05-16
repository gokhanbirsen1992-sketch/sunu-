import { motion, useTransform, type MotionValue } from "framer-motion";

type Props = { progress: MotionValue<number> };

/**
 * KATMAN 3 — Hücresel
 *
 * Hepatosit: bazolateral kapı (OATP1B1/B3) → UGT1A1 (ER) →
 * apikal kapı (MRP2). Scroll'la 3 kapı sırayla aktive olur,
 * bir bilirubin molekülü sol → orta → sağ akar.
 */
export function HepatocyteVisual({ progress }: Props) {
  const gate1 = useTransform(progress, [0, 0.12, 0.35, 0.55], [0.25, 1, 1, 0.5]);
  const gate2 = useTransform(progress, [0.25, 0.45, 0.65, 0.8], [0.25, 1, 1, 0.55]);
  const gate3 = useTransform(progress, [0.55, 0.75, 0.95], [0.25, 1, 1]);

  // Bilirubin molecule trajectory across the hepatocyte
  const billiX = useTransform(progress, [0.05, 0.45, 0.95], [-78, 0, 78]);
  const billiColor = useTransform(
    progress,
    [0, 0.45, 0.55, 1],
    ["#f5b942", "#f5b942", "#7dd3fc", "#7dd3fc"],
  );

  // Pulsing rings inside ER during conjugation
  const erPulseScale = useTransform(progress, [0.3, 0.5, 0.7], [0.8, 1.15, 0.95]);
  const erPulseOpacity = useTransform(progress, [0.3, 0.5, 0.7], [0.4, 1, 0.5]);

  return (
    <svg
      viewBox="-100 -100 200 200"
      className="visual-svg"
      preserveAspectRatio="xMidYMid meet"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="cellBg" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="rgba(52, 211, 153, 0.10)" />
          <stop offset="100%" stopColor="rgba(192, 132, 252, 0.10)" />
        </linearGradient>
      </defs>

      {/* Hepatocyte body */}
      <rect
        x={-78}
        y={-46}
        width={156}
        height={92}
        rx={14}
        fill="url(#cellBg)"
        stroke="rgba(236, 232, 223, 0.22)"
        strokeWidth={0.7}
      />

      {/* Outside-cell labels */}
      <text
        x={-88}
        y={-58}
        textAnchor="middle"
        fontFamily="ui-sans-serif, system-ui"
        fontSize={4.6}
        fill="rgba(236, 232, 223, 0.5)"
      >
        SİNUSOİD
      </text>
      <text
        x={88}
        y={-58}
        textAnchor="middle"
        fontFamily="ui-sans-serif, system-ui"
        fontSize={4.6}
        fill="rgba(236, 232, 223, 0.5)"
      >
        SAFRA
      </text>

      {/* GATE 1 — Bazolateral: OATP1B1 / OATP1B3 */}
      <motion.g style={{ opacity: gate1 }}>
        <rect
          x={-80}
          y={-20}
          width={4}
          height={40}
          fill="#34d399"
          rx={1}
        />
        <circle cx={-78} cy={-12} r={2.6} fill="#34d399" />
        <circle cx={-78} cy={12} r={2.6} fill="#34d399" />
        <text
          x={-65}
          y={-30}
          textAnchor="start"
          fontFamily="ui-sans-serif, system-ui"
          fontSize={5.2}
          fontWeight={600}
          fill="#34d399"
        >
          OATP1B1 / B3
        </text>
        <text
          x={-65}
          y={-23}
          textAnchor="start"
          fontFamily="ui-sans-serif, system-ui"
          fontSize={4}
          fill="rgba(52, 211, 153, 0.7)"
        >
          bazolateral kapı
        </text>
      </motion.g>

      {/* GATE 2 — Endoplazmik retikulum: UGT1A1 */}
      <motion.g style={{ opacity: gate2 }}>
        <ellipse
          cx={0}
          cy={5}
          rx={28}
          ry={20}
          fill="rgba(192, 132, 252, 0.18)"
          stroke="#c084fc"
          strokeWidth={0.7}
        />
        <motion.ellipse
          cx={0}
          cy={5}
          rx={28}
          ry={20}
          fill="none"
          stroke="#c084fc"
          strokeWidth={0.4}
          style={{
            scale: erPulseScale,
            opacity: erPulseOpacity,
            transformOrigin: "center",
            transformBox: "fill-box",
          }}
        />
        <text
          x={0}
          y={-22}
          textAnchor="middle"
          fontFamily="ui-sans-serif, system-ui"
          fontSize={5.4}
          fontWeight={600}
          fill="#c084fc"
        >
          UGT1A1
        </text>
        <text
          x={0}
          y={-15}
          textAnchor="middle"
          fontFamily="ui-sans-serif, system-ui"
          fontSize={4}
          fill="rgba(192, 132, 252, 0.7)"
        >
          endoplazmik retikulum
        </text>
        <text
          x={0}
          y={12}
          textAnchor="middle"
          fontFamily="ui-sans-serif, system-ui"
          fontSize={4.4}
          fill="#c084fc"
          opacity={0.85}
        >
          +UDP-glukuronik asit
        </text>
      </motion.g>

      {/* GATE 3 — Apikal: MRP2 / ABCC2 */}
      <motion.g style={{ opacity: gate3 }}>
        <rect
          x={76}
          y={-20}
          width={4}
          height={40}
          fill="#84cc16"
          rx={1}
        />
        <rect
          x={71}
          y={-8}
          width={8}
          height={16}
          fill="#84cc16"
          rx={1.5}
        />
        <text
          x={65}
          y={-30}
          textAnchor="end"
          fontFamily="ui-sans-serif, system-ui"
          fontSize={5.2}
          fontWeight={600}
          fill="#84cc16"
        >
          MRP2 / ABCC2
        </text>
        <text
          x={65}
          y={-23}
          textAnchor="end"
          fontFamily="ui-sans-serif, system-ui"
          fontSize={4}
          fill="rgba(132, 204, 22, 0.7)"
        >
          apikal kapı · ATP'li pompa
        </text>
      </motion.g>

      {/* Traveling bilirubin */}
      <motion.circle
        cy={0}
        r={4.5}
        style={{ x: billiX, fill: billiColor }}
      />
      <motion.circle
        cy={0}
        r={9}
        style={{ x: billiX, fill: billiColor }}
        opacity={0.18}
      />
    </svg>
  );
}
