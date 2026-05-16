import { motion, useTransform, type MotionValue } from "framer-motion";

type Props = { progress: MotionValue<number> };

/**
 * KATMAN 2 — Kimya
 *
 * Bilirubin 4 pirol halkalı, katlanmış (4Z,15Z). 460 nm mavi ışık
 * çift bağa çarpınca konfigürasyon 4Z,15E'ye dönüşür — molekül açılır.
 */
export function BilirubinVisual({ progress }: Props) {
  const foldedOpacity = useTransform(
    progress,
    [0, 0.38, 0.58],
    [1, 1, 0],
  );
  const beamOpacity = useTransform(progress, [0.3, 0.45, 0.75], [0, 1, 0.35]);
  const beamY = useTransform(progress, [0.3, 0.55], [-120, 0]);
  const flashOpacity = useTransform(progress, [0.48, 0.55, 0.62], [0, 1, 0]);
  const unfoldedOpacity = useTransform(progress, [0.55, 0.78], [0, 1]);
  const labelFolded = useTransform(progress, [0, 0.45, 0.5], [1, 1, 0]);
  const labelUnfolded = useTransform(progress, [0.55, 0.7], [0, 1]);

  return (
    <svg
      viewBox="-100 -100 200 200"
      className="visual-svg"
      preserveAspectRatio="xMidYMid meet"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="beamGrad" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#60a5fa" stopOpacity="0" />
          <stop offset="40%" stopColor="#60a5fa" stopOpacity="0.55" />
          <stop offset="100%" stopColor="#60a5fa" stopOpacity="0" />
        </linearGradient>
        <radialGradient id="flashGrad">
          <stop offset="0%" stopColor="#fff" stopOpacity="1" />
          <stop offset="60%" stopColor="#fff" stopOpacity="0.5" />
          <stop offset="100%" stopColor="#fff" stopOpacity="0" />
        </radialGradient>
      </defs>

      {/* Phototherapy beam (460 nm) */}
      <motion.g style={{ opacity: beamOpacity, y: beamY }}>
        <rect x={-10} y={-110} width={20} height={220} fill="url(#beamGrad)" />
        <text
          x={-14}
          y={-86}
          textAnchor="end"
          fontFamily="ui-sans-serif, system-ui"
          fontSize={5.4}
          fill="#7dd3fc"
          opacity={0.7}
        >
          460 nm
        </text>
      </motion.g>

      {/* Photon impact flash */}
      <motion.circle
        cx={0}
        cy={0}
        r={18}
        fill="url(#flashGrad)"
        style={{ opacity: flashOpacity }}
      />

      {/* FOLDED bilirubin — 4 pirol halkası katlanmış, 6 H-bağı */}
      <motion.g style={{ opacity: foldedOpacity }}>
        <FoldedBilirubin />
      </motion.g>

      {/* UNFOLDED bilirubin — 4Z,15E + lumirubin yolu */}
      <motion.g style={{ opacity: unfoldedOpacity }}>
        <UnfoldedBilirubin />
      </motion.g>

      <motion.text
        x={0}
        y={82}
        textAnchor="middle"
        fontFamily="ui-sans-serif, system-ui"
        fontSize={5.4}
        fill="#f5b942"
        opacity={0.7}
        style={{ opacity: labelFolded }}
      >
        4Z,15Z · katlanmış · suda çözünmez
      </motion.text>
      <motion.text
        x={0}
        y={82}
        textAnchor="middle"
        fontFamily="ui-sans-serif, system-ui"
        fontSize={5.4}
        fill="#7dd3fc"
        style={{ opacity: labelUnfolded }}
      >
        4Z,15E · foto-izomer · suda çözünür
      </motion.text>
    </svg>
  );
}

/** Helper: a single pyrrole-like ring (pentagon) with an N label and color. */
function PyrroleRing({
  x,
  y,
  rotation = 0,
  fill = "rgba(245, 185, 66, 0.25)",
  stroke = "#f5b942",
}: {
  x: number;
  y: number;
  rotation?: number;
  fill?: string;
  stroke?: string;
}) {
  const r = 9;
  const pts = Array.from({ length: 5 }).map((_, i) => {
    const a = ((i * 72 - 90 + rotation) * Math.PI) / 180;
    return [Math.cos(a) * r, Math.sin(a) * r];
  });
  const path = pts.map((p, i) => `${i === 0 ? "M" : "L"} ${p[0]} ${p[1]}`).join(" ") + " Z";
  return (
    <g transform={`translate(${x},${y})`}>
      <path d={path} fill={fill} stroke={stroke} strokeWidth={0.6} />
      <text
        textAnchor="middle"
        y={2}
        fontSize={5.4}
        fontFamily="ui-sans-serif, system-ui"
        fontWeight={600}
        fill={stroke}
      >
        N
      </text>
    </g>
  );
}

function FoldedBilirubin() {
  // Compact arrangement: 4 rings clustered with internal H-bonds
  return (
    <g>
      {/* Hydrogen bonds — dashed yellow lines */}
      <g stroke="#fde68a" strokeWidth={0.5} strokeDasharray="2 2" opacity={0.7}>
        <line x1={-22} y1={-12} x2={-7} y2={-12} />
        <line x1={7} y1={-12} x2={22} y2={-12} />
        <line x1={-22} y1={12} x2={-7} y2={12} />
        <line x1={7} y1={12} x2={22} y2={12} />
        <line x1={-15} y1={-3} x2={-15} y2={3} />
        <line x1={15} y1={-3} x2={15} y2={3} />
      </g>
      {/* 4 pyrrole rings */}
      <PyrroleRing x={-30} y={-12} rotation={0} />
      <PyrroleRing x={-10} y={-12} rotation={180} />
      <PyrroleRing x={10} y={-12} rotation={0} />
      <PyrroleRing x={30} y={-12} rotation={180} />
      {/* Methenyl bridges between */}
      <g stroke="#f5b942" strokeWidth={0.8} fill="none">
        <line x1={-21} y1={-12} x2={-19} y2={-12} />
        <line x1={-1} y1={-12} x2={1} y2={-12} />
        <line x1={19} y1={-12} x2={21} y2={-12} />
      </g>
      {/* Propionic acid side chains tucked inside */}
      <g stroke="#f5b942" strokeWidth={0.6} fill="none" opacity={0.7}>
        <path d="M -8 -3 C -4 4, 4 4, 8 -3" />
      </g>
    </g>
  );
}

function UnfoldedBilirubin() {
  // Extended arrangement: rings spread, central bridge rotated, H-bonds gone
  return (
    <g>
      {/* 4 pyrrole rings spread horizontally, central bridge rotated */}
      <PyrroleRing
        x={-46}
        y={-6}
        rotation={0}
        fill="rgba(125, 211, 252, 0.18)"
        stroke="#7dd3fc"
      />
      <PyrroleRing
        x={-17}
        y={4}
        rotation={180}
        fill="rgba(125, 211, 252, 0.18)"
        stroke="#7dd3fc"
      />
      <PyrroleRing
        x={17}
        y={-4}
        rotation={0}
        fill="rgba(125, 211, 252, 0.18)"
        stroke="#7dd3fc"
      />
      <PyrroleRing
        x={46}
        y={6}
        rotation={180}
        fill="rgba(125, 211, 252, 0.18)"
        stroke="#7dd3fc"
      />
      {/* Open methenyl bridges — central one shows rotation */}
      <g stroke="#7dd3fc" strokeWidth={0.8} fill="none">
        <line x1={-37} y1={-6} x2={-26} y2={4} />
        <line x1={-8} y1={4} x2={8} y2={-4} />
        <line x1={26} y1={-4} x2={37} y2={6} />
      </g>
      {/* Carboxyl groups exposed */}
      <g fill="#7dd3fc" opacity={0.85}>
        <circle cx={-58} cy={-12} r={2.4} />
        <circle cx={58} cy={12} r={2.4} />
      </g>
      <g
        fontFamily="ui-sans-serif, system-ui"
        fontSize={4.2}
        fill="#7dd3fc"
        opacity={0.85}
      >
        <text x={-62} y={-16} textAnchor="middle">
          COOH
        </text>
        <text x={62} y={16} textAnchor="middle">
          COOH
        </text>
      </g>
    </g>
  );
}
