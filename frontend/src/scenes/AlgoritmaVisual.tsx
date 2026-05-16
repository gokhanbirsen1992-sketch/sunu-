import { motion, useTransform, type MotionValue } from "framer-motion";

type Props = { progress: MotionValue<number> };

/**
 * KATMAN 12.7 — Yatak başı ayırıcı tanı algoritması
 *
 * Hiperbilirubinemi → direkt/indirekt → ... → sendrom.
 * Branches reveal sequentially with scroll.
 */
export function AlgoritmaVisual({ progress }: Props) {
  const root = useTransform(progress, [0.0, 0.1], [0, 1]);
  const branch1 = useTransform(progress, [0.15, 0.25], [0, 1]);
  const branch2 = useTransform(progress, [0.3, 0.4], [0, 1]);
  const direct = useTransform(progress, [0.4, 0.5], [0, 1]);
  const indirect = useTransform(progress, [0.5, 0.6], [0, 1]);
  const cn1 = useTransform(progress, [0.62, 0.72], [0, 1]);
  const cn2 = useTransform(progress, [0.7, 0.8], [0, 1]);
  const gilbert = useTransform(progress, [0.78, 0.86], [0, 1]);
  const dj = useTransform(progress, [0.86, 0.93], [0, 1]);
  const rotor = useTransform(progress, [0.92, 1.0], [0, 1]);

  const highlight = useTransform(progress, [0.85, 1], [0, 1]);

  return (
    <svg
      viewBox="-100 -100 200 200"
      className="visual-svg"
      preserveAspectRatio="xMidYMid meet"
      aria-hidden="true"
    >
      {/* Root: total bilirubin elevated */}
      <motion.g style={{ opacity: root }}>
        <rect x={-32} y={-90} width={64} height={16} rx={3} fill="rgba(148, 163, 184, 0.18)" stroke="#94a3b8" strokeWidth={0.5} />
        <text
          x={0}
          y={-79}
          textAnchor="middle"
          fontFamily="ui-sans-serif, system-ui"
          fontSize={4.6}
          fontWeight={600}
          fill="#cbd5e1"
        >
          Bilirubin ↑
        </text>
      </motion.g>

      {/* First split: indirect vs direct */}
      <motion.g style={{ opacity: branch1 }} stroke="#94a3b8" strokeWidth={0.5}>
        <line x1={0} y1={-74} x2={-46} y2={-50} />
        <line x1={0} y1={-74} x2={46} y2={-50} />
        <text x={-25} y={-58} fontFamily="ui-sans-serif, system-ui" fontSize={3.6} fill="#94a3b8">D/T ‹ %20</text>
        <text x={25} y={-58} fontFamily="ui-sans-serif, system-ui" fontSize={3.6} fill="#94a3b8">D/T › %20</text>
      </motion.g>

      <motion.g style={{ opacity: indirect }}>
        <rect x={-72} y={-50} width={52} height={14} rx={3} fill="rgba(245, 185, 66, 0.18)" stroke="#f5b942" strokeWidth={0.5} />
        <text
          x={-46}
          y={-40}
          textAnchor="middle"
          fontFamily="ui-sans-serif, system-ui"
          fontSize={4.2}
          fontWeight={600}
          fill="#fde68a"
        >
          İNDİREKT
        </text>
      </motion.g>

      <motion.g style={{ opacity: direct }}>
        <rect x={20} y={-50} width={52} height={14} rx={3} fill="rgba(132, 204, 22, 0.18)" stroke="#84cc16" strokeWidth={0.5} />
        <text
          x={46}
          y={-40}
          textAnchor="middle"
          fontFamily="ui-sans-serif, system-ui"
          fontSize={4.2}
          fontWeight={600}
          fill="#bef264"
        >
          DİREKT
        </text>
      </motion.g>

      {/* Second split — indirect side: hemoliz check */}
      <motion.g style={{ opacity: branch2 }} stroke="#94a3b8" strokeWidth={0.4}>
        <line x1={-46} y1={-36} x2={-46} y2={-22} />
        <text x={-44} y={-26} fontFamily="ui-sans-serif, system-ui" fontStyle="italic" fontSize={3.2} fill="#94a3b8">
          hemoliz?
        </text>
      </motion.g>

      <motion.g style={{ opacity: branch2 }}>
        <rect x={-72} y={-22} width={52} height={11} rx={2} fill="rgba(15, 23, 42, 0.5)" stroke="#94a3b8" strokeWidth={0.4} />
        <text
          x={-46}
          y={-14}
          textAnchor="middle"
          fontFamily="ui-sans-serif, system-ui"
          fontSize={3.6}
          fill="#94a3b8"
        >
          Coombs negatif, retik normal
        </text>
        <text
          x={-46}
          y={-1}
          textAnchor="middle"
          fontFamily="ui-sans-serif, system-ui"
          fontStyle="italic"
          fontSize={3}
          fill="rgba(148,163,184,0.7)"
        >
          → UGT1A1 koridoru
        </text>
      </motion.g>

      {/* Leaves: CN1 / CN2 / Gilbert */}
      <motion.g style={{ opacity: cn1 }}>
        <line x1={-46} y1={5} x2={-80} y2={28} stroke="#f59e0b" strokeWidth={0.45} />
        <rect x={-100} y={28} width={42} height={20} rx={3} fill="rgba(245, 158, 11, 0.22)" stroke="#f59e0b" strokeWidth={0.7} />
        <text x={-79} y={38} textAnchor="middle" fontFamily="ui-sans-serif, system-ui" fontSize={4.2} fontWeight={700} fill="#fef3c7">CN tip I</text>
        <text x={-79} y={45} textAnchor="middle" fontFamily="ui-sans-serif, system-ui" fontSize={3.2} fill="#fbbf24">UGT1A1 = 0</text>
      </motion.g>

      <motion.g style={{ opacity: cn2 }}>
        <line x1={-46} y1={5} x2={-46} y2={28} stroke="#fb923c" strokeWidth={0.45} />
        <rect x={-66} y={28} width={42} height={20} rx={3} fill="rgba(251, 146, 60, 0.18)" stroke="#fb923c" strokeWidth={0.5} />
        <text x={-45} y={38} textAnchor="middle" fontFamily="ui-sans-serif, system-ui" fontSize={4.2} fontWeight={600} fill="#fed7aa">CN tip II</text>
        <text x={-45} y={45} textAnchor="middle" fontFamily="ui-sans-serif, system-ui" fontSize={3.2} fill="#fdba74">~%10 aktivite</text>
      </motion.g>

      <motion.g style={{ opacity: gilbert }}>
        <line x1={-46} y1={5} x2={-12} y2={28} stroke="#fde68a" strokeWidth={0.45} />
        <rect x={-32} y={28} width={42} height={20} rx={3} fill="rgba(253, 230, 138, 0.14)" stroke="#fde68a" strokeWidth={0.5} />
        <text x={-11} y={38} textAnchor="middle" fontFamily="ui-sans-serif, system-ui" fontSize={4.2} fontWeight={600} fill="#fef3c7">Gilbert</text>
        <text x={-11} y={45} textAnchor="middle" fontFamily="ui-sans-serif, system-ui" fontSize={3.2} fill="#fde68a">~%30 aktivite</text>
      </motion.g>

      {/* Leaves: DJ / Rotor */}
      <motion.g style={{ opacity: dj }}>
        <line x1={46} y1={-36} x2={30} y2={28} stroke="#84cc16" strokeWidth={0.45} />
        <rect x={14} y={28} width={42} height={20} rx={3} fill="rgba(132, 204, 22, 0.18)" stroke="#84cc16" strokeWidth={0.5} />
        <text x={35} y={38} textAnchor="middle" fontFamily="ui-sans-serif, system-ui" fontSize={4.2} fontWeight={600} fill="#d9f99d">Dubin-J.</text>
        <text x={35} y={45} textAnchor="middle" fontFamily="ui-sans-serif, system-ui" fontSize={3.2} fill="#bef264">MRP2 yok</text>
      </motion.g>

      <motion.g style={{ opacity: rotor }}>
        <line x1={46} y1={-36} x2={68} y2={28} stroke="#06b6d4" strokeWidth={0.45} />
        <rect x={50} y={28} width={42} height={20} rx={3} fill="rgba(6, 182, 212, 0.18)" stroke="#06b6d4" strokeWidth={0.5} />
        <text x={71} y={38} textAnchor="middle" fontFamily="ui-sans-serif, system-ui" fontSize={4.2} fontWeight={600} fill="#a5f3fc">Rotor</text>
        <text x={71} y={45} textAnchor="middle" fontFamily="ui-sans-serif, system-ui" fontSize={3.2} fill="#67e8f9">OATP × 2</text>
      </motion.g>

      {/* Highlight: Yıldız's path — CN1 */}
      <motion.g style={{ opacity: highlight }}>
        <rect
          x={-104}
          y={24}
          width={50}
          height={28}
          rx={4}
          fill="none"
          stroke="#fef3c7"
          strokeWidth={0.8}
          strokeDasharray="3 2"
        />
        <text
          x={-79}
          y={62}
          textAnchor="middle"
          fontFamily="'Cormorant Garamond', serif"
          fontStyle="italic"
          fontSize={5.2}
          fill="#fef3c7"
        >
          ✦ Yıldız
        </text>
      </motion.g>

      {/* Title */}
      <text
        x={0}
        y={-85}
        fontFamily="ui-sans-serif, system-ui"
        fontSize={3.4}
        letterSpacing={2}
        textAnchor="middle"
        fill="rgba(236, 232, 223, 0.45)"
        transform="translate(0, -10)"
      >
        YATAK BAŞI · AYIRICI TANI
      </text>
    </svg>
  );
}
