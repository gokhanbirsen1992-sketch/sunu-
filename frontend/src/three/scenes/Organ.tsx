import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import type { SceneProps } from "../types";
import { localProgress, lerp, smoothstep } from "../types";

/**
 * KATMAN 5 / 7 / 9 — Karaciğer + Lobül + Embriyo.
 *
 * Procedural karaciğer: yumuşak ellipsoid + lobül altıgenleri yüzeyde,
 * portal-triad işaretleri. Embriyoloji fazında küçük "bud" görünür ve
 * büyüyerek tam organ olur.
 */
export function Organ({ scroll, range }: SceneProps) {
  const groupRef = useRef<THREE.Group>(null);
  const liverRef = useRef<THREE.Mesh>(null);
  const lobuleRef = useRef<THREE.Group>(null);

  // Hex lobule positions on a 2D grid (we'll wrap them onto liver surface)
  const lobules = useMemo(() => {
    const result: Array<{ pos: [number, number, number]; size: number }> = [];
    const rows = 6;
    const cols = 8;
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const u = c / (cols - 1) - 0.5;
        const v = r / (rows - 1) - 0.5;
        // Map to sphere-ish liver surface
        const theta = u * Math.PI * 0.8;
        const phi = v * Math.PI * 0.5;
        const radius = 2;
        const x = radius * Math.cos(phi) * Math.sin(theta);
        const y = radius * Math.sin(phi);
        const z = radius * Math.cos(phi) * Math.cos(theta);
        result.push({
          pos: [x, y, z],
          size: 0.12 + Math.abs(u) * 0.04,
        });
      }
    }
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
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.08 + lp * 0.5;
      groupRef.current.rotation.x = lerp(0.2, -0.1, lp);
    }
    if (liverRef.current) {
      // Embryology phase: liver grows from a small bud
      const grow = smoothstep(0, 0.3, lp);
      liverRef.current.scale.set(
        1.0 + grow * 0.4,
        0.75 + grow * 0.25,
        0.85 + grow * 0.15,
      );
    }
    if (lobuleRef.current) {
      // Lobules emerge in mid-phase
      const lob = smoothstep(0.3, 0.55, lp);
      lobuleRef.current.visible = lob > 0.05;
      lobuleRef.current.children.forEach((child, i) => {
        const m = (child as THREE.Mesh).material as THREE.MeshStandardMaterial;
        m.opacity = lob * 0.85;
        (child as THREE.Mesh).scale.setScalar(0.5 + lob * 0.6 + Math.sin(state.clock.elapsedTime * 2 + i * 0.2) * 0.04);
      });
    }
  });

  return (
    <group ref={groupRef}>
      {/* Liver body */}
      <mesh ref={liverRef} scale={[1, 0.75, 0.85]}>
        <sphereGeometry args={[1.8, 48, 32]} />
        <meshStandardMaterial
          color="#7a3328"
          emissive="#5a1f15"
          emissiveIntensity={0.18}
          roughness={0.7}
          metalness={0.05}
        />
      </mesh>
      {/* Wireframe overlay for "anatomical" feel */}
      <mesh scale={[1.005, 0.755, 0.855]}>
        <sphereGeometry args={[1.8, 24, 16]} />
        <meshBasicMaterial color="#f97316" wireframe transparent opacity={0.12} />
      </mesh>
      {/* Lobule markers */}
      <group ref={lobuleRef}>
        {lobules.map((l, i) => (
          <mesh key={i} position={l.pos}>
            <sphereGeometry args={[l.size, 8, 8]} />
            <meshStandardMaterial
              color="#fb923c"
              emissive="#fb923c"
              emissiveIntensity={0.5}
              transparent
              opacity={0.7}
            />
          </mesh>
        ))}
      </group>
    </group>
  );
}
