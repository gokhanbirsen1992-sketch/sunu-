import {
  motion,
  useTransform,
  type MotionValue,
} from "framer-motion";
import { layerTheme } from "../layerThemes";

type Props = {
  id: string;
  progress: MotionValue<number>;
};

type Pattern =
  | "rings"
  | "particles"
  | "wave"
  | "tree"
  | "timeline"
  | "hex"
  | "flow"
  | "star"
  | "twocircles"
  | "glyph";

const PATTERN_BY_ID: Record<string, Pattern> = {
  "4": "tree",
  "5": "rings",
  "6": "timeline",
  "7": "hex",
  "8": "particles",
  "9": "flow",
  "10": "rings",
  "11": "wave",
  "12.1": "star",
  "12.2": "wave",
  "12.3": "wave",
  "12.4": "wave",
  "12.5": "particles",
  "12.6": "twocircles",
  "12.7": "tree",
  "12.8": "glyph",
  "12.9": "glyph",
};

export function AmbientVisual({ id, progress }: Props) {
  const theme = layerTheme(id);
  const pattern: Pattern = PATTERN_BY_ID[id] ?? "rings";
  switch (pattern) {
    case "rings":
      return <RingsPattern progress={progress} accent={theme.accent} />;
    case "particles":
      return <ParticlesPattern progress={progress} accent={theme.accent} />;
    case "wave":
      return (
        <WavePattern
          progress={progress}
          accent={theme.accent}
          intensity={id === "12.3" ? 1.4 : id === "12.4" ? 0.9 : id === "12.2" ? 0.5 : 1}
        />
      );
    case "tree":
      return <TreePattern progress={progress} accent={theme.accent} />;
    case "timeline":
      return <TimelinePattern progress={progress} accent={theme.accent} />;
    case "hex":
      return <HexPattern progress={progress} accent={theme.accent} />;
    case "flow":
      return <FlowPattern progress={progress} accent={theme.accent} />;
    case "star":
      return <StarPattern progress={progress} accent={theme.accent} />;
    case "twocircles":
      return <TwoCirclesPattern progress={progress} accent={theme.accent} />;
    case "glyph":
      return (
        <GlyphPattern
          progress={progress}
          accent={theme.accent}
          glyph={theme.glyph}
          label={theme.label}
        />
      );
  }
}

function svgFrame(children: React.ReactNode) {
  return (
    <svg
      viewBox="-100 -100 200 200"
      className="visual-svg"
      preserveAspectRatio="xMidYMid meet"
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

/* ------------------------- Patterns ------------------------- */

function RingsPattern({
  progress,
  accent,
}: {
  progress: MotionValue<number>;
  accent: string;
}) {
  const scale = useTransform(progress, [0, 1], [0.65, 1.35]);
  const opacity = useTransform(progress, [0, 0.2, 0.85, 1], [0, 0.9, 0.9, 0.3]);
  const rotation = useTransform(progress, [0, 1], [0, 24]);
  const rings = [10, 22, 38, 56, 76, 96];
  return svgFrame(
    <motion.g
      style={{
        scale,
        opacity,
        rotate: rotation,
        transformOrigin: "center",
      }}
    >
      {rings.map((r, i) => (
        <circle
          key={i}
          cx={0}
          cy={0}
          r={r}
          fill="none"
          stroke={accent}
          strokeWidth={0.6}
          opacity={1 - i * 0.13}
        />
      ))}
      <circle cx={0} cy={0} r={4} fill={accent} opacity={0.9} />
    </motion.g>,
  );
}

function ParticlesPattern({
  progress,
  accent,
}: {
  progress: MotionValue<number>;
  accent: string;
}) {
  const opacity = useTransform(progress, [0, 0.25, 0.85, 1], [0, 1, 1, 0.3]);
  const drift = useTransform(progress, [0, 1], [0, 18]);
  const rotation = useTransform(progress, [0, 1], [0, 8]);
  const dots = Array.from({ length: 64 }).map((_, i) => {
    const seed = (i * 0.6180339887) % 1;
    const angle = i * 137.5;
    const r = 16 + seed * 80;
    const rad = (angle * Math.PI) / 180;
    return {
      x: Math.cos(rad) * r,
      y: Math.sin(rad) * r,
      r: 0.6 + seed * 1.6,
      o: 0.3 + seed * 0.6,
    };
  });
  return svgFrame(
    <motion.g
      style={{ opacity, y: drift, rotate: rotation, transformOrigin: "center" }}
    >
      {dots.map((d, i) => (
        <circle key={i} cx={d.x} cy={d.y} r={d.r} fill={accent} opacity={d.o} />
      ))}
    </motion.g>,
  );
}

function WavePattern({
  progress,
  accent,
  intensity = 1,
}: {
  progress: MotionValue<number>;
  accent: string;
  intensity?: number;
}) {
  const shift = useTransform(progress, [0, 1], [0, -100]);
  const opacity = useTransform(progress, [0, 0.25, 0.85, 1], [0, 1, 1, 0.3]);
  const wavePath = (amp: number, freq: number, phase: number) => {
    const pts: string[] = [];
    for (let x = -120; x <= 220; x += 4) {
      const y =
        Math.sin((x / 100) * Math.PI * freq + phase) * amp * intensity;
      pts.push(`${x === -120 ? "M" : "L"} ${x} ${y}`);
    }
    return pts.join(" ");
  };
  return svgFrame(
    <motion.g style={{ opacity, x: shift }}>
      <path
        d={wavePath(8, 1.2, 0)}
        fill="none"
        stroke={accent}
        strokeWidth={0.9}
        opacity={0.85}
      />
      <path
        d={wavePath(14, 0.8, 1)}
        fill="none"
        stroke={accent}
        strokeWidth={0.7}
        opacity={0.55}
        transform="translate(0, 18)"
      />
      <path
        d={wavePath(20, 0.5, 2)}
        fill="none"
        stroke={accent}
        strokeWidth={0.5}
        opacity={0.35}
        transform="translate(0, -22)"
      />
      <path
        d={wavePath(10, 1.6, 1.5)}
        fill="none"
        stroke={accent}
        strokeWidth={0.6}
        opacity={0.55}
        transform="translate(0, 40)"
      />
      <path
        d={wavePath(11, 1, 0.4)}
        fill="none"
        stroke={accent}
        strokeWidth={0.6}
        opacity={0.5}
        transform="translate(0, -42)"
      />
    </motion.g>,
  );
}

function TreePattern({
  progress,
  accent,
}: {
  progress: MotionValue<number>;
  accent: string;
}) {
  const drawProgress = useTransform(progress, [0, 0.7], [0, 1]);
  // Render branches with strokeDasharray tied to drawProgress
  const dash = useTransform(drawProgress, (v) => `${v * 200} 200`);
  const opacity = useTransform(progress, [0, 0.2, 0.85, 1], [0, 1, 1, 0.4]);

  return svgFrame(
    <motion.g style={{ opacity }} stroke={accent} fill="none" strokeWidth={0.7}>
      {/* trunk */}
      <motion.line x1={0} y1={88} x2={0} y2={20} style={{ strokeDasharray: dash }} />
      {/* Level 1 branches */}
      <motion.line x1={0} y1={20} x2={-44} y2={-12} style={{ strokeDasharray: dash }} />
      <motion.line x1={0} y1={20} x2={44} y2={-12} style={{ strokeDasharray: dash }} />
      {/* Level 2 */}
      <motion.line x1={-44} y1={-12} x2={-70} y2={-44} style={{ strokeDasharray: dash }} />
      <motion.line x1={-44} y1={-12} x2={-18} y2={-44} style={{ strokeDasharray: dash }} />
      <motion.line x1={44} y1={-12} x2={18} y2={-44} style={{ strokeDasharray: dash }} />
      <motion.line x1={44} y1={-12} x2={70} y2={-44} style={{ strokeDasharray: dash }} />
      {/* Level 3 */}
      <motion.line x1={-70} y1={-44} x2={-82} y2={-72} style={{ strokeDasharray: dash }} />
      <motion.line x1={-70} y1={-44} x2={-58} y2={-72} style={{ strokeDasharray: dash }} />
      <motion.line x1={-18} y1={-44} x2={-30} y2={-72} style={{ strokeDasharray: dash }} />
      <motion.line x1={-18} y1={-44} x2={-6} y2={-72} style={{ strokeDasharray: dash }} />
      <motion.line x1={18} y1={-44} x2={6} y2={-72} style={{ strokeDasharray: dash }} />
      <motion.line x1={18} y1={-44} x2={30} y2={-72} style={{ strokeDasharray: dash }} />
      <motion.line x1={70} y1={-44} x2={58} y2={-72} style={{ strokeDasharray: dash }} />
      <motion.line x1={70} y1={-44} x2={82} y2={-72} style={{ strokeDasharray: dash }} />
      {/* Leaf nodes */}
      <motion.g style={{ opacity: drawProgress }}>
        {[-82, -58, -30, -6, 6, 30, 58, 82].map((x, i) => (
          <circle key={i} cx={x} cy={-72} r={2.4} fill={accent} stroke="none" />
        ))}
      </motion.g>
    </motion.g>,
  );
}

function TimelinePattern({
  progress,
  accent,
}: {
  progress: MotionValue<number>;
  accent: string;
}) {
  const lineScale = useTransform(progress, [0.05, 0.55], [0, 1]);
  const opacity = useTransform(progress, [0, 0.2, 0.85, 1], [0, 1, 1, 0.4]);
  // Precompute fade-in transforms for each year marker at top level
  const o0 = useTransform(progress, [0.1, 0.2], [0, 1]);
  const o1 = useTransform(progress, [0.2, 0.3], [0, 1]);
  const o2 = useTransform(progress, [0.3, 0.4], [0, 1]);
  const o3 = useTransform(progress, [0.4, 0.5], [0, 1]);
  const o4 = useTransform(progress, [0.5, 0.6], [0, 1]);
  const years: Array<{ year: number; o: MotionValue<number> }> = [
    { year: 1903, o: o0 },
    { year: 1948, o: o1 },
    { year: 1952, o: o2 },
    { year: 1954, o: o3 },
    { year: 1962, o: o4 },
  ];
  return svgFrame(
    <motion.g style={{ opacity }}>
      <motion.line
        x1={-90}
        y1={0}
        x2={90}
        y2={0}
        stroke={accent}
        strokeWidth={0.8}
        style={{ scaleX: lineScale, transformOrigin: "left center" }}
      />
      {years.map(({ year, o }, i) => {
        const x = -90 + (i / (years.length - 1)) * 180;
        return (
          <motion.g key={year} style={{ opacity: o }}>
            <circle cx={x} cy={0} r={3.2} fill={accent} />
            <text
              x={x}
              y={-12}
              textAnchor="middle"
              fontFamily="ui-sans-serif, system-ui"
              fontSize={6}
              fill={accent}
              opacity={0.85}
            >
              {year}
            </text>
            <line
              x1={x}
              y1={6}
              x2={x}
              y2={18}
              stroke={accent}
              strokeWidth={0.4}
              opacity={0.4}
            />
          </motion.g>
        );
      })}
    </motion.g>,
  );
}

function HexPattern({
  progress,
  accent,
}: {
  progress: MotionValue<number>;
  accent: string;
}) {
  const rotation = useTransform(progress, [0, 1], [-12, 12]);
  const opacity = useTransform(progress, [0, 0.2, 0.85, 1], [0, 1, 1, 0.4]);
  const scale = useTransform(progress, [0, 1], [0.85, 1.1]);
  const hexagons: { cx: number; cy: number; r: number; o: number }[] = [];
  const r = 18;
  const dx = r * Math.sqrt(3);
  const dy = r * 1.5;
  for (let row = -3; row <= 3; row++) {
    for (let col = -3; col <= 3; col++) {
      const cx = col * dx + (row % 2 ? dx / 2 : 0);
      const cy = row * dy;
      const dist = Math.hypot(cx, cy);
      if (dist < 95) hexagons.push({ cx, cy, r, o: 1 - dist / 110 });
    }
  }
  const hexPath = (cx: number, cy: number, size: number) => {
    const pts: string[] = [];
    for (let i = 0; i < 6; i++) {
      const a = ((60 * i - 30) * Math.PI) / 180;
      pts.push(`${cx + Math.cos(a) * size} ${cy + Math.sin(a) * size}`);
    }
    return `M ${pts[0]} L ${pts.slice(1).join(" L ")} Z`;
  };
  return svgFrame(
    <motion.g
      style={{
        opacity,
        scale,
        rotate: rotation,
        transformOrigin: "center",
      }}
    >
      {hexagons.map((h, i) => (
        <path
          key={i}
          d={hexPath(h.cx, h.cy, h.r * 0.92)}
          fill="none"
          stroke={accent}
          strokeWidth={0.5}
          opacity={h.o * 0.7}
        />
      ))}
    </motion.g>,
  );
}

function FlowPattern({
  progress,
  accent,
}: {
  progress: MotionValue<number>;
  accent: string;
}) {
  const offset = useTransform(progress, [0, 1], [0, -200]);
  const opacity = useTransform(progress, [0, 0.25, 0.85, 1], [0, 1, 1, 0.4]);
  // Two concentric loops (enterohepatic) with dashed traveling lines
  return svgFrame(
    <motion.g style={{ opacity }}>
      {/* outer loop */}
      <motion.ellipse
        cx={0}
        cy={0}
        rx={75}
        ry={50}
        fill="none"
        stroke={accent}
        strokeWidth={0.8}
        strokeDasharray="6 6"
        style={{ strokeDashoffset: offset }}
      />
      {/* inner loop */}
      <motion.ellipse
        cx={0}
        cy={0}
        rx={45}
        ry={28}
        fill="none"
        stroke={accent}
        strokeWidth={0.6}
        strokeDasharray="3 5"
        opacity={0.7}
        style={{ strokeDashoffset: offset }}
      />
      {/* Arrows */}
      <text
        x={75}
        y={0}
        textAnchor="middle"
        dominantBaseline="middle"
        fontSize={12}
        fill={accent}
      >
        ▶
      </text>
      <text
        x={-75}
        y={0}
        textAnchor="middle"
        dominantBaseline="middle"
        fontSize={12}
        fill={accent}
      >
        ◀
      </text>
      {/* Labels */}
      <text
        x={0}
        y={-58}
        textAnchor="middle"
        fontFamily="ui-sans-serif, system-ui"
        fontSize={5.4}
        fill={accent}
        opacity={0.75}
      >
        KARACİĞER
      </text>
      <text
        x={0}
        y={62}
        textAnchor="middle"
        fontFamily="ui-sans-serif, system-ui"
        fontSize={5.4}
        fill={accent}
        opacity={0.75}
      >
        BAĞIRSAK
      </text>
    </motion.g>,
  );
}

function StarPattern({
  progress,
  accent,
}: {
  progress: MotionValue<number>;
  accent: string;
}) {
  const pulse = useTransform(progress, [0, 0.5, 1], [0.7, 1.2, 0.9]);
  const opacity = useTransform(progress, [0, 0.25, 0.85, 1], [0, 1, 1, 0.5]);
  const rays = useTransform(progress, [0, 1], [0, 45]);
  return svgFrame(
    <>
      <motion.g
        style={{ opacity, scale: pulse, transformOrigin: "center" }}
      >
        <defs>
          <radialGradient id="star-glow">
            <stop offset="0%" stopColor="#fff" stopOpacity="1" />
            <stop offset="40%" stopColor={accent} stopOpacity="0.9" />
            <stop offset="100%" stopColor={accent} stopOpacity="0" />
          </radialGradient>
        </defs>
        <circle cx={0} cy={0} r={62} fill="url(#star-glow)" />
        <circle cx={0} cy={0} r={18} fill="#fff" opacity={0.95} />
      </motion.g>
      <motion.g
        style={{
          opacity,
          rotate: rays,
          transformOrigin: "center",
        }}
        stroke={accent}
        strokeWidth={0.6}
        opacity={0.5}
      >
        {Array.from({ length: 8 }).map((_, i) => {
          const a = (i * 45 * Math.PI) / 180;
          return (
            <line
              key={i}
              x1={Math.cos(a) * 26}
              y1={Math.sin(a) * 26}
              x2={Math.cos(a) * 90}
              y2={Math.sin(a) * 90}
            />
          );
        })}
      </motion.g>
    </>,
  );
}

function TwoCirclesPattern({
  progress,
  accent,
}: {
  progress: MotionValue<number>;
  accent: string;
}) {
  const opacity = useTransform(progress, [0, 0.25, 0.85, 1], [0, 1, 1, 0.4]);
  const separation = useTransform(progress, [0, 0.5, 1], [10, 30, 22]);
  return svgFrame(
    <motion.g style={{ opacity }}>
      <motion.circle
        cy={0}
        r={40}
        fill="none"
        stroke={accent}
        strokeWidth={0.8}
        style={{ cx: useTransform(separation, (v) => -v) }}
      />
      <motion.circle
        cy={0}
        r={40}
        fill="none"
        stroke={accent}
        strokeWidth={0.8}
        style={{ cx: separation }}
      />
      <motion.circle
        cy={0}
        r={4}
        fill={accent}
        style={{ cx: useTransform(separation, (v) => -v) }}
      />
      <motion.circle
        cy={0}
        r={4}
        fill={accent}
        style={{ cx: separation }}
      />
      <text
        x={0}
        y={62}
        textAnchor="middle"
        fontFamily="ui-sans-serif, system-ui"
        fontSize={5.4}
        fill={accent}
        opacity={0.7}
      >
        OATP1B1 · OATP1B3
      </text>
    </motion.g>,
  );
}

function GlyphPattern({
  progress,
  accent,
  glyph,
  label,
}: {
  progress: MotionValue<number>;
  accent: string;
  glyph: string;
  label: string;
}) {
  const opacity = useTransform(progress, [0, 0.25, 0.85, 1], [0, 1, 1, 0.4]);
  const scale = useTransform(progress, [0, 1], [0.92, 1.08]);
  const ringScale = useTransform(progress, [0, 1], [0.9, 1.4]);
  const ringOpacity = useTransform(
    progress,
    [0, 0.3, 0.7, 1],
    [0, 0.6, 0.6, 0.1],
  );
  return svgFrame(
    <motion.g style={{ opacity }}>
      <motion.circle
        cx={0}
        cy={0}
        r={60}
        fill="none"
        stroke={accent}
        strokeWidth={0.5}
        opacity={0.3}
        style={{
          scale: ringScale,
          opacity: ringOpacity,
          transformOrigin: "center",
        }}
      />
      <motion.text
        x={0}
        y={6}
        textAnchor="middle"
        dominantBaseline="middle"
        fontFamily="'Cormorant Garamond', serif"
        fontWeight={500}
        fontSize={120}
        fill={accent}
        style={{ scale, transformOrigin: "center" }}
      >
        {glyph}
      </motion.text>
      <text
        x={0}
        y={78}
        textAnchor="middle"
        fontFamily="ui-sans-serif, system-ui"
        fontSize={5.6}
        letterSpacing={3.5}
        fill={accent}
        opacity={0.65}
      >
        {label.toUpperCase()}
      </text>
    </motion.g>,
  );
}
