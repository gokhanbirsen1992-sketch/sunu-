import { useMemo } from "react";

type Star = {
  cx: number;
  cy: number;
  r: number;
  o: number;
  d: number;
};

function seededStars(count: number, seed = 42): Star[] {
  let s = seed;
  const rand = () => {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
  return Array.from({ length: count }, () => ({
    cx: rand() * 100,
    cy: rand() * 100,
    r: rand() * 1.4 + 0.2,
    o: rand() * 0.6 + 0.2,
    d: rand() * 6 + 2,
  }));
}

export function Cosmos() {
  const stars = useMemo(() => seededStars(180), []);
  return (
    <div className="cosmos" aria-hidden="true">
      <svg viewBox="0 0 100 100" preserveAspectRatio="none">
        {stars.map((star, i) => (
          <circle
            key={i}
            className="star"
            cx={star.cx}
            cy={star.cy}
            r={star.r * 0.12}
            style={{
              opacity: star.o,
              animation: `twinkle ${star.d}s ease-in-out ${star.d * 0.3}s infinite`,
              ["--o" as never]: star.o,
            }}
          />
        ))}
      </svg>
    </div>
  );
}
