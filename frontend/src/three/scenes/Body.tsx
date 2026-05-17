import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import type { SceneProps } from "../types";
import { localProgress, lerp, smoothstep } from "../types";

/**
 * KATMAN 11 / 12.1 — Yıldız bedeni + fototerapi.
 *
 * Bebek silueti yıldızsı sarı bir glow olarak (capsule + sphere head).
 * Üstten mavi fototerapi ışın koni iner. Vücut kademeli olarak sararıp
 * sonra ışık altında biraz açılır.
 */
export function Body({ scroll, range }: SceneProps) {
  const groupRef = useRef<THREE.Group>(null);
  const bodyRef = useRef<THREE.Mesh>(null);
  const headRef = useRef<THREE.Mesh>(null);
  const haloRef = useRef<THREE.Mesh>(null);
  const beamRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    const p = scroll.current.value;
    const lp = localProgress(p, range);
    const vis =
      smoothstep(range[0] - 0.04, range[0] + 0.02, p) *
      (1 - smoothstep(range[1] - 0.02, range[1] + 0.04, p));

    if (groupRef.current) {
      groupRef.current.visible = vis > 0.01;
      groupRef.current.rotation.y = lerp(-0.3, 0.3, lp);
    }
    // Yellow intensity peaks mid-section (Kramer 5), then phototherapy reduces
    const yellow = smoothstep(0.0, 0.4, lp) * (1 - smoothstep(0.7, 1.0, lp) * 0.4);

    if (bodyRef.current) {
      const m = bodyRef.current.material as THREE.MeshStandardMaterial;
      m.emissiveIntensity = 0.4 + yellow * 0.6;
    }
    if (headRef.current) {
      const m = headRef.current.material as THREE.MeshStandardMaterial;
      m.emissiveIntensity = 0.4 + yellow * 0.6;
    }
    if (haloRef.current) {
      const m = haloRef.current.material as THREE.MeshBasicMaterial;
      m.opacity = yellow * 0.45;
      haloRef.current.scale.setScalar(1 + Math.sin(state.clock.elapsedTime * 1.5) * 0.04);
    }
    if (beamRef.current) {
      const phototherapy = smoothstep(0.4, 0.7, lp);
      const m = beamRef.current.material as THREE.MeshBasicMaterial;
      m.opacity = phototherapy * 0.55;
      beamRef.current.position.y = lerp(4, 1.5, phototherapy);
    }
  });

  return (
    <group ref={groupRef}>
      {/* Yellow halo around baby */}
      <mesh ref={haloRef} position={[0, 0, 0]}>
        <sphereGeometry args={[2, 24, 24]} />
        <meshBasicMaterial
          color="#f5b942"
          transparent
          opacity={0.2}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </mesh>

      {/* Body capsule */}
      <mesh ref={bodyRef} position={[0, -0.4, 0]}>
        <capsuleGeometry args={[0.55, 1.0, 8, 16]} />
        <meshStandardMaterial
          color="#fef3c7"
          emissive="#f5b942"
          emissiveIntensity={0.6}
          roughness={0.4}
          metalness={0.1}
        />
      </mesh>
      {/* Head */}
      <mesh ref={headRef} position={[0, 0.9, 0]}>
        <sphereGeometry args={[0.42, 24, 24]} />
        <meshStandardMaterial
          color="#fef3c7"
          emissive="#f5b942"
          emissiveIntensity={0.6}
          roughness={0.4}
          metalness={0.1}
        />
      </mesh>

      {/* Phototherapy beam cone */}
      <mesh ref={beamRef} position={[0, 4, 0]}>
        <coneGeometry args={[1.5, 4, 32, 1, true]} />
        <meshBasicMaterial
          color="#60a5fa"
          transparent
          opacity={0}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
          side={THREE.DoubleSide}
        />
      </mesh>

      {/* Incubator frame */}
      <mesh position={[0, 0.2, 0]}>
        <boxGeometry args={[3.2, 2.4, 1.8]} />
        <meshBasicMaterial color="#1a1a2e" wireframe transparent opacity={0.4} />
      </mesh>
    </group>
  );
}
