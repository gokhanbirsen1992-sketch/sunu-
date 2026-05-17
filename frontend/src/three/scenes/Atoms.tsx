import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Text } from "@react-three/drei";
import * as THREE from "three";
import type { SceneProps } from "../types";
import { localProgress, lerp, smoothstep } from "../types";

/**
 * KATMAN 1 sonu — Hidrojen, Karbon (Hoyle), Demir atomları.
 *
 * 3D mekanda dağılmış atomlar. Kamera yaklaştıkça etiketler okunur.
 * Karbon halkası (Hoyle resonance) ortada vurgulu.
 */
export function Atoms({ scroll, range }: SceneProps) {
  const groupRef = useRef<THREE.Group>(null);

  // Pre-generate atom positions
  const atoms = useMemo(() => {
    const result: Array<{
      pos: [number, number, number];
      color: string;
      label: string;
      size: number;
    }> = [];
    // Hydrogen cloud — small blue dots far apart
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
      });
    }
    // Carbon — Hoyle: 3 helium → 1 carbon. 3 atoms triangulated
    [
      [-1.8, 0.5, 0.5],
      [1.6, 0.7, 0.8],
      [-0.2, -1.4, -0.4],
    ].forEach((p) => {
      result.push({
        pos: p as [number, number, number],
        color: "#a78bfa",
        label: "C",
        size: 0.22,
      });
    });
    // Iron — supernova remnants
    [
      [2.6, 1.6, 1.2],
      [-2.8, -0.8, 1.4],
      [0.4, 2.2, -1.2],
    ].forEach((p) => {
      result.push({
        pos: p as [number, number, number],
        color: "#fb923c",
        label: "Fe",
        size: 0.2,
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
      {atoms.map((a, i) => (
        <group key={i} position={a.pos}>
          {/* Atom core */}
          <mesh>
            <sphereGeometry args={[a.size, 16, 16]} />
            <meshStandardMaterial
              color={a.color}
              emissive={a.color}
              emissiveIntensity={0.8}
              roughness={0.4}
              metalness={0.1}
            />
          </mesh>
          {/* Glow halo */}
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
          {a.label !== "H" && (
            <Text
              position={[0, a.size + 0.18, 0]}
              fontSize={0.16}
              color={a.color}
              anchorX="center"
              anchorY="bottom"
              outlineWidth={0.005}
              outlineColor="#000"
            >
              {a.label}
            </Text>
          )}
        </group>
      ))}
    </group>
  );
}
