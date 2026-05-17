import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Text } from "@react-three/drei";
import * as THREE from "three";
import type { SceneProps } from "../types";
import { localProgress, lerp, smoothstep } from "../types";

/**
 * KATMAN 3 / 12.5 / 12.6 — Hepatosit.
 *
 * Yumuşak rounded-box hücre. Sol yüzünde 2 yeşil OATP transporter,
 * sağ yüzünde 1 yeşil-mavi MRP2 pompa, ortada mor ER (UGT1A1).
 * Bilirubin molekülü soldan sağa akar.
 */
export function Cell({ scroll, range }: SceneProps) {
  const groupRef = useRef<THREE.Group>(null);
  const biliRef = useRef<THREE.Mesh>(null);
  const erRef = useRef<THREE.Mesh>(null);
  const leftGateRef = useRef<THREE.Group>(null);
  const rightGateRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    const p = scroll.current.value;
    const lp = localProgress(p, range);
    const vis =
      smoothstep(range[0] - 0.04, range[0] + 0.02, p) *
      (1 - smoothstep(range[1] - 0.02, range[1] + 0.04, p));

    if (groupRef.current) {
      groupRef.current.visible = vis > 0.01;
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.1;
    }

    if (biliRef.current) {
      biliRef.current.position.x = lerp(-2.2, 2.2, lp);
      biliRef.current.position.y = Math.sin(lp * Math.PI) * 0.2;
      const m = biliRef.current.material as THREE.MeshStandardMaterial;
      m.color.set(lp > 0.5 ? "#7dd3fc" : "#f5b942");
      m.emissive.set(lp > 0.5 ? "#7dd3fc" : "#f5b942");
    }

    // ER pulses when conjugation phase
    if (erRef.current) {
      const erPulse = smoothstep(0.35, 0.55, lp) * (1 - smoothstep(0.65, 0.85, lp));
      erRef.current.scale.setScalar(0.9 + erPulse * 0.2 + Math.sin(state.clock.elapsedTime * 3) * 0.03 * erPulse);
      const m = erRef.current.material as THREE.MeshStandardMaterial;
      m.emissiveIntensity = 0.4 + erPulse * 0.6;
    }

    if (leftGateRef.current) {
      const phase = 1 - smoothstep(0.15, 0.35, lp);
      leftGateRef.current.scale.setScalar(0.9 + phase * 0.25);
    }
    if (rightGateRef.current) {
      const phase = smoothstep(0.65, 0.85, lp);
      rightGateRef.current.scale.setScalar(0.9 + phase * 0.25);
    }
  });

  return (
    <group ref={groupRef}>
      {/* Cell body — rounded box */}
      <mesh>
        <boxGeometry args={[5, 2.8, 1.8]} />
        <meshStandardMaterial
          color="#3b3a55"
          transparent
          opacity={0.25}
          roughness={0.7}
          metalness={0.1}
        />
      </mesh>
      <mesh>
        <boxGeometry args={[5.04, 2.84, 1.84]} />
        <meshBasicMaterial color="#a78bfa" wireframe transparent opacity={0.15} />
      </mesh>

      {/* Basolateral gates (left) */}
      <group ref={leftGateRef} position={[-2.5, 0, 0]}>
        <mesh position={[0, 0.7, 0]}>
          <cylinderGeometry args={[0.15, 0.15, 0.4, 12]} />
          <meshStandardMaterial color="#34d399" emissive="#34d399" emissiveIntensity={0.7} />
        </mesh>
        <mesh position={[0, -0.7, 0]}>
          <cylinderGeometry args={[0.15, 0.15, 0.4, 12]} />
          <meshStandardMaterial color="#34d399" emissive="#34d399" emissiveIntensity={0.7} />
        </mesh>
        <Text position={[-0.4, 1.6, 0]} fontSize={0.14} color="#34d399" anchorX="center">
          OATP1B1/B3
        </Text>
      </group>

      {/* ER + UGT1A1 (center) */}
      <mesh ref={erRef}>
        <sphereGeometry args={[0.6, 24, 16]} />
        <meshStandardMaterial
          color="#c084fc"
          emissive="#c084fc"
          emissiveIntensity={0.4}
          roughness={0.5}
          metalness={0.2}
          transparent
          opacity={0.9}
        />
      </mesh>
      <Text position={[0, 0.95, 0]} fontSize={0.16} color="#c084fc" anchorX="center">
        UGT1A1
      </Text>

      {/* Apical gate (right) — MRP2 */}
      <group ref={rightGateRef} position={[2.5, 0, 0]}>
        <mesh>
          <cylinderGeometry args={[0.18, 0.18, 0.5, 12]} />
          <meshStandardMaterial color="#84cc16" emissive="#84cc16" emissiveIntensity={0.7} />
        </mesh>
        <Text position={[0.4, 0.6, 0]} fontSize={0.14} color="#84cc16" anchorX="center">
          MRP2
        </Text>
      </group>

      {/* Traveling bilirubin */}
      <mesh ref={biliRef} position={[-2.2, 0, 0]}>
        <sphereGeometry args={[0.16, 16, 16]} />
        <meshStandardMaterial
          color="#f5b942"
          emissive="#f5b942"
          emissiveIntensity={0.8}
        />
      </mesh>
    </group>
  );
}
