import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Sparkles } from "@react-three/drei";
import * as THREE from "three";
import type { SceneProps } from "../types";
import { localProgress, lerp, smoothstep } from "../types";

/**
 * KATMAN 13 — Kapanış. Kamera geri çekilir, Yıldız bir tek yıldız olarak
 * kalır, sonra kozmosa kavuşur.
 */
export function Pullback({ scroll, range }: SceneProps) {
  const groupRef = useRef<THREE.Group>(null);
  const starRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    const p = scroll.current.value;
    const lp = localProgress(p, range);
    const vis = smoothstep(range[0] - 0.04, range[0] + 0.02, p);

    if (groupRef.current) {
      groupRef.current.visible = vis > 0.01;
    }
    if (starRef.current) {
      // Star pulses gently
      const pulse = 1 + Math.sin(state.clock.elapsedTime * 1.2) * 0.06;
      starRef.current.scale.setScalar(lerp(2.5, 0.4, lp) * pulse);
      const m = starRef.current.material as THREE.MeshStandardMaterial;
      m.emissiveIntensity = lerp(1.4, 0.8, lp);
    }
  });

  return (
    <group ref={groupRef}>
      {/* Yıldız as a single bright star */}
      <mesh ref={starRef} position={[0, 0, 0]}>
        <sphereGeometry args={[0.6, 32, 32]} />
        <meshStandardMaterial
          color="#fef3c7"
          emissive="#f5b942"
          emissiveIntensity={1.2}
          roughness={0.3}
          metalness={0.1}
        />
      </mesh>
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[1.4, 24, 24]} />
        <meshBasicMaterial
          color="#f5b942"
          transparent
          opacity={0.25}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </mesh>
      <Sparkles
        count={300}
        scale={[30, 30, 30]}
        size={3}
        speed={0.3}
        opacity={0.7}
        color="#ffffff"
      />
    </group>
  );
}
