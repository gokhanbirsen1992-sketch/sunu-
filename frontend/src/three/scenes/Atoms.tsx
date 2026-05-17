import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Html, Float } from "@react-three/drei";
import * as THREE from "three";
import type { SceneProps } from "../types";
import { localProgress, lerp, smoothstep } from "../types";

/**
 * KATMAN 1 sonu — Hidrojen, Karbon (Hoyle), Demir atomları.
 */
export function Atoms({ scroll, range }: SceneProps) {
  const groupRef = useRef<THREE.Group>(null);

  const atoms = useMemo(() => {
    const result: Array<{
      pos: [number, number, number];
      color: string;
      label: string;
      size: number;
      labeled: boolean;
    }> = [];
    let s = 11;
    const rand = () => {
      s = (s * 9301 + 49297) % 233280;
      return s / 233280;
    };
    for (let i = 0; i < 40; i++) {
      const r = 4 + rand() * 5;
      const a = rand() * Math.PI * 2;
      const e = (rand() - 0.5) * 1.5;
      result.push({
        pos: [Math.cos(a) * r, e, Math.sin(a) * r - 2],
        color: "#7dd3fc",
        label: "H",
        size: 0.08,
        labeled: false,
      });
    }
    [
      [-1.6, 0.4, 0.5],
      [1.5, 0.6, 0.8],
      [-0.2, -1.3, -0.4],
    ].forEach((p) => {
      result.push({
        pos: p as [number, number, number],
        color: "#a78bfa",
        label: "C",
        size: 0.24,
        labeled: true,
      });
    });
    [
      [2.4, 1.5, 1.0],
      [-2.6, -0.7, 1.2],
      [0.3, 2.0, -1.0],
    ].forEach((p) => {
      result.push({
        pos: p as [number, number, number],
        color: "#fb923c",
        label: "Fe",
        size: 0.22,
        labeled: true,
      });
    });
    return result;
  }, []);

  useFrame((state) => {
    const p = scroll.current.value;
    const lp = localProgress(p, range);
    const vis =
      smoothstep(range[0] - 0.04, range[0] + 0.02, p) *
      (1 - smoothstep(range[1] - 0.02, range[1] + 0.04, p));

    if (groupRef.current) {
      groupRef.current.visible = vis > 0.01;
      groupRef.current.position.set(
        lerp(2, -2, lp),
        lerp(-0.5, 0.5, lp),
        lerp(-2, 6, lp),
      );
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.05 + lp * 0.4;
    }
  });

  return (
    <group ref={groupRef}>
      <Float speed={1.0} rotationIntensity={0.2} floatIntensity={0.3}>
        {atoms.map((a, i) => (
          <group key={i} position={a.pos}>
            <mesh>
              <sphereGeometry args={[a.size, 20, 20]} />
              <meshPhysicalMaterial
                color={a.color}
                emissive={a.color}
                emissiveIntensity={0.7}
                roughness={0.3}
                metalness={0.15}
                clearcoat={0.6}
              />
            </mesh>
            <mesh>
              <sphereGeometry args={[a.size * 2.2, 12, 12]} />
              <meshBasicMaterial
                color={a.color}
                transparent
                opacity={0.18}
                blending={THREE.AdditiveBlending}
                depthWrite={false}
              />
            </mesh>
            {a.labeled && (
              <Html
                position={[0, a.size + 0.3, 0]}
                center
                style={{ pointerEvents: "none" }}
              >
                <div
                  style={{
                    fontFamily: "Fraunces, serif",
                    fontSize: 16,
                    fontStyle: "italic",
                    color: a.color,
                    textShadow: `0 0 12px ${a.color}, 0 0 24px ${a.color}`,
                    fontWeight: 500,
                  }}
                >
                  {a.label}
                </div>
              </Html>
            )}
          </group>
        ))}
      </Float>
    </group>
  );
}
