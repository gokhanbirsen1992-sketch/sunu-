import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Sparkles } from "@react-three/drei";
import * as THREE from "three";
import type { SceneProps } from "../types";
import { localProgress, lerp, smoothstep } from "../types";

/**
 * KATMAN 1 — Kozmoloji. drei Sparkles ×2 + Big Bang flash + nebula halo.
 */
export function Cosmos({ scroll, range }: SceneProps) {
  const groupRef = useRef<THREE.Group>(null);
  const flashRef = useRef<THREE.Mesh>(null);
  const haloRef = useRef<THREE.Mesh>(null);

  useFrame(() => {
    const p = scroll.current.value;
    const lp = localProgress(p, range);
    const vis =
      smoothstep(range[0] - 0.05, range[0], p) *
      (1 - smoothstep(range[1], range[1] + 0.05, p));

    if (groupRef.current) {
      groupRef.current.visible = vis > 0.01;
      groupRef.current.position.z = lerp(-2, 8, lp);
      groupRef.current.rotation.z = lp * 0.4;
    }
    if (flashRef.current) {
      const flashStrength = Math.max(0, 1 - Math.abs(lp - 0.12) * 8);
      const m = flashRef.current.material as THREE.MeshBasicMaterial;
      m.opacity = flashStrength * vis;
      flashRef.current.scale.setScalar(
        lerp(0.4, 3, lp) * (1 + flashStrength * 2),
      );
    }
    if (haloRef.current) {
      const m = haloRef.current.material as THREE.MeshBasicMaterial;
      m.opacity = vis * (0.3 + smoothstep(0.0, 0.6, lp) * 0.4);
      haloRef.current.scale.setScalar(lerp(2, 6, lp));
    }
  });

  return (
    <group ref={groupRef} visible={true} position={[0, 0, -2]}>
      <Sparkles
        count={400}
        scale={[40, 40, 40]}
        size={3}
        speed={0.25}
        opacity={0.9}
        color="#ffffff"
      />
      <Sparkles
        count={140}
        scale={[18, 18, 18]}
        size={6}
        speed={0.4}
        opacity={1}
        color="#fef3c7"
      />
      <mesh ref={flashRef} position={[0, 0, 0]} scale={0.5}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshBasicMaterial
          color="#fef3c7"
          transparent
          opacity={0.4}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </mesh>
      <mesh ref={haloRef} position={[0, 0, -2]} scale={3}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshBasicMaterial
          color="#a78bfa"
          transparent
          opacity={0.25}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
          side={THREE.BackSide}
        />
      </mesh>
    </group>
  );
}
