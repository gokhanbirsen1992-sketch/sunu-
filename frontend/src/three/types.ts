import type { ScrollProgressRef } from "../hooks/useScrollProgress";

/**
 * Each scene gets the global scroll progress + its own range. Inside useFrame,
 * compute local progress 0..1 within that range. Outside the range the scene
 * is hidden via opacity / visible flag.
 */
export type SceneProps = {
  scroll: ScrollProgressRef;
  range: [number, number];
};

/** Helper: clamp + map global progress to local 0..1 within a range. */
export function localProgress(
  global: number,
  range: [number, number],
): number {
  const [a, b] = range;
  if (global <= a) return 0;
  if (global >= b) return 1;
  return (global - a) / (b - a);
}

/** Smoothstep — easier blend curves. */
export function smoothstep(edge0: number, edge1: number, x: number): number {
  const t = Math.max(0, Math.min(1, (x - edge0) / (edge1 - edge0)));
  return t * t * (3 - 2 * t);
}

/** Linear interpolation. */
export function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}
