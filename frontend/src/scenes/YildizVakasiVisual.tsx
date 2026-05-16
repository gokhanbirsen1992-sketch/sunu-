import { useEffect, useState } from "react";
import {
  motion,
  useMotionValueEvent,
  useTransform,
  type MotionValue,
} from "framer-motion";

type Props = { progress: MotionValue<number> };

/**
 * KATMAN 12.1 — Yıldız Vaka Derinleşmesi
 *
 * Yıldız 4 günlük, fototerapi altında. Total 28, direkt 1.6 (oran %5.7),
 * Coombs negatif, retikülosit %3. Tablo: indirekt hiperbilirubinemi
 * + hemoliz YOK + safra ağacı normal → UGT1A1 koridoruna girilir.
 */
export function YildizVakasiVisual({ progress }: Props) {
  // Phase 1: incubator + baby
  const babyGlowOpacity = useTransform(progress, [0, 0.1, 1], [0, 1, 1]);
  const beamOpacity = useTransform(progress, [0.1, 0.25, 1], [0, 0.65, 0.65]);

  // Phase 2: lab values appear one by one
  const lab1 = useTransform(progress, [0.2, 0.3], [0, 1]);
  const lab2 = useTransform(progress, [0.32, 0.42], [0, 1]);
  const lab3 = useTransform(progress, [0.44, 0.54], [0, 1]);
  const lab4 = useTransform(progress, [0.56, 0.66], [0, 1]);
  const lab5 = useTransform(progress, [0.68, 0.78], [0, 1]);

  // Phase 3: arrow points to UGT1A1
  const conclusionOpacity = useTransform(progress, [0.8, 0.95], [0, 1]);

  // Bilirubin trajectory: 28 → 24
  const bili = useTransform(progress, [0.0, 0.5, 1], [28, 26, 24]);
  const [biliText, setBiliText] = useState("28");
  useMotionValueEvent(bili, "change", (v) => setBiliText(v.toFixed(0)));
  useEffect(() => setBiliText(Math.round(bili.get()).toString()), [bili]);

  return (
    <svg
      viewBox="-100 -100 200 200"
      className="visual-svg"
      preserveAspectRatio="xMidYMid meet"
      aria-hidden="true"
    >
      <defs>
        <radialGradient id="baby-glow-vaka">
          <stop offset="0%" stopColor="#fff7e0" stopOpacity="1" />
          <stop offset="40%" stopColor="#f5b942" stopOpacity="0.8" />
          <stop offset="100%" stopColor="#f5b942" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="vaka-beam" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#60a5fa" stopOpacity="0" />
          <stop offset="100%" stopColor="#60a5fa" stopOpacity="0.6" />
        </linearGradient>
      </defs>

      {/* Incubator outline */}
      <rect
        x={-78}
        y={-58}
        width={156}
        height={64}
        rx={8}
        fill="none"
        stroke="rgba(236, 232, 223, 0.18)"
        strokeWidth={0.5}
      />
      <text
        x={-78}
        y={-64}
        fontFamily="ui-sans-serif, system-ui"
        fontSize={3.4}
        letterSpacing={1.6}
        fill="rgba(236, 232, 223, 0.45)"
      >
        İNKÜBATÖR · 96. SAAT
      </text>

      {/* Phototherapy beam */}
      <motion.rect
        x={-40}
        y={-58}
        width={80}
        height={26}
        fill="url(#vaka-beam)"
        style={{ opacity: beamOpacity }}
      />
      <motion.text
        x={-40}
        y={-44}
        fontFamily="ui-sans-serif, system-ui"
        fontSize={3.4}
        fill="#7dd3fc"
        opacity={0.65}
        style={{ opacity: beamOpacity }}
      >
        FOTOTERAPİ · 460 nm
      </motion.text>

      {/* Baby silhouette with glow */}
      <motion.g style={{ opacity: babyGlowOpacity }}>
        <circle cx={0} cy={-20} r={28} fill="url(#baby-glow-vaka)" />
        <ellipse cx={0} cy={-22} rx={14} ry={10} fill="#fef3c7" opacity={0.95} />
        <circle cx={0} cy={-32} r={5.5} fill="#fef3c7" />
        <text
          x={0}
          y={-19}
          textAnchor="middle"
          fontFamily="'Cormorant Garamond', serif"
          fontStyle="italic"
          fontSize={6}
          fill="rgba(0, 0, 0, 0.55)"
        >
          Yıldız
        </text>
      </motion.g>

      {/* Lab panel — bottom */}
      <g transform="translate(-80, 14)">
        <text
          fontFamily="ui-sans-serif, system-ui"
          fontSize={3.8}
          letterSpacing={2}
          fill="rgba(236, 232, 223, 0.55)"
        >
          LABORATUVAR
        </text>

        {/* Lab rows */}
        <LabRow y={10} label="Total bilirubin" value="28" unit="mg/dL" hot opacity={lab1} />
        <LabRow y={20} label="Direkt bilirubin" value="1.6" unit="mg/dL" opacity={lab2} />
        <LabRow y={30} label="D/T oranı" value="%5.7" unit="(< 20%)" opacity={lab3} />
        <LabRow y={40} label="Retikülosit" value="%3" unit="normal" opacity={lab4} />
        <LabRow y={50} label="Coombs (direkt)" value="negatif" unit="" cool opacity={lab5} />
      </g>

      {/* Conclusion arrow */}
      <motion.g style={{ opacity: conclusionOpacity }}>
        <text
          x={48}
          y={56}
          fontFamily="'Cormorant Garamond', serif"
          fontStyle="italic"
          fontSize={6}
          fill="#facc15"
          textAnchor="end"
        >
          → UGT1A1 koridoru
        </text>
        <text
          x={48}
          y={64}
          fontFamily="ui-sans-serif, system-ui"
          fontSize={3.6}
          fill="rgba(250, 204, 21, 0.7)"
          textAnchor="end"
        >
          hemoliz yok · safra ağacı normal
        </text>
      </motion.g>

      {/* Bilirubin number in upper right (trajectory) */}
      <g transform="translate(60, -82)">
        <text
          fontFamily="ui-sans-serif, system-ui"
          fontSize={3.2}
          letterSpacing={1.4}
          fill="rgba(236,232,223,0.55)"
        >
          BİLİRUBİN
        </text>
        <motion.text
          y={16}
          fontFamily="'Cormorant Garamond', serif"
          fontWeight={500}
          fontSize={22}
          fill="#fef3c7"
          textAnchor="start"
        >
          {biliText}
        </motion.text>
        <text
          x={28}
          y={16}
          fontFamily="ui-sans-serif, system-ui"
          fontSize={3.2}
          fill="rgba(236,232,223,0.5)"
        >
          mg/dL
        </text>
      </g>
    </svg>
  );
}

function LabRow({
  y,
  label,
  value,
  unit,
  hot,
  cool,
  opacity,
}: {
  y: number;
  label: string;
  value: string;
  unit: string;
  hot?: boolean;
  cool?: boolean;
  opacity: MotionValue<number>;
}) {
  const color = hot ? "#facc15" : cool ? "#34d399" : "rgba(236,232,223,0.85)";
  return (
    <motion.g style={{ opacity }}>
      <line
        x1={0}
        y1={y - 2}
        x2={160}
        y2={y - 2}
        stroke="rgba(236, 232, 223, 0.08)"
        strokeWidth={0.3}
      />
      <text
        x={0}
        y={y + 4}
        fontFamily="ui-sans-serif, system-ui"
        fontSize={3.6}
        fill="rgba(236, 232, 223, 0.75)"
      >
        {label}
      </text>
      <text
        x={100}
        y={y + 4}
        fontFamily="ui-sans-serif, system-ui"
        fontSize={4.4}
        fontWeight={hot ? 600 : 500}
        fill={color}
        textAnchor="end"
      >
        {value}
      </text>
      <text
        x={104}
        y={y + 4}
        fontFamily="ui-sans-serif, system-ui"
        fontSize={3}
        fill="rgba(236, 232, 223, 0.4)"
      >
        {unit}
      </text>
    </motion.g>
  );
}
