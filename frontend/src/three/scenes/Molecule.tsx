import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import type { SceneProps } from "../types";
import { localProgress, lerp, smoothstep } from "../types";

/**
 * KATMAN 2/10 — Bilirubin molekülü 3D.
 *
 * 4 pirol halkası (toruslar) bir zigzag zincirde dizilmiş. Başlangıçta
 * katlanmış (compact), scroll'la fototerapi mavi ışını iner ve molekül
 * açılır (4Z,15E foto-izomer).
 */
export function Molecule({ scroll, range }: SceneProps) {
  const groupRef = useRef<THREE.Group>(null);
  const beamRef = useRef<THREE.Mesh>(null);
  const ring2Ref = useRef<THREE.Group>(null);
  const ring3Ref = useRef<THREE.Group>(null);

  useFrame((state) => {
    const p = scroll.current.value;
    const lp = localProgress(p, range);
    const vis =
      smoothstep(range[0] - 0.04, range[0] + 0.02, p) *
      (1 - smoothstep(range[1] - 0.02, range[1] + 0.04, p));

    if (groupRef.current) {
      groupRef.current.visible = vis > 0.01;
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.18;
      groupRef.current.rotation.x = lerp(0.1, -0.2, lp);
      groupRef.current.scale.setScalar(lerp(0.6, 1.1, lp));
    }

    // Phototherapy beam descends mid-section
    if (beamRef.current) {
      const beamPhase = Math.max(0, Math.min(1, (lp - 0.35) / 0.25));
      beamRef.current.position.y = lerp(2.5, 0, beamPhase);
      const m = beamRef.current.material as THREE.MeshBasicMaterial;
      m.opacity = beamPhase * (1 - smoothstep(0.7, 1, lp)) * vis * 0.85;
    }

    // Unfold: rings 2 & 3 flip when light hits (mid-range onward)
    const unfold = smoothstep(0.5, 0.8, lp);
    if (ring2Ref.current) {
      ring2Ref.current.rotation.z = lerp(0, Math.PI, unfold);
      ring2Ref.current.position.y = lerp(-0.4, 0.3, unfold);
    }
    if (ring3Ref.current) {
      ring3Ref.current.rotation.z = lerp(0, -Math.PI, unfold);
      ring3Ref.current.position.y = lerp(0.4, -0.3, unfold);
    }
  });

  return (
    <group ref={groupRef}>
      <PyrroleRing position={[-1.2, 0, 0]} color="#f5b942" />
      <group ref={ring2Ref}>
        <PyrroleRing position={[-0.4, -0.4, 0]} color="#f5b942" />
      </group>
      <group ref={ring3Ref}>
        <PyrroleRing position={[0.4, 0.4, 0]} color="#f5b942" />
      </group>
      <PyrroleRing position={[1.2, 0, 0]} color="#f5b942" />

      {/* Methenyl bridges between rings */}
      <Bridge from={[-1.2, 0, 0]} to={[-0.4, -0.4, 0]} />
      <Bridge from={[-0.4, -0.4, 0]} to={[0.4, 0.4, 0]} />
      <Bridge from={[0.4, 0.4, 0]} to={[1.2, 0, 0]} />

      {/* Phototherapy beam from above */}
      <mesh ref={beamRef} position={[0, 2.5, 0]}>
        <cylinderGeometry args={[0.05, 0.5, 4, 16, 1, true]} />
        <meshBasicMaterial
          color="#60a5fa"
          transparent
          opacity={0}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
          side={THREE.DoubleSide}
        />
      </mesh>
    </group>
  );
}

function PyrroleRing({
  position,
  color,
}: {
  position: [number, number, number];
  color: string;
}) {
  return (
    <group position={position}>
      {/* Ring */}
      <mesh>
        <torusGeometry args={[0.28, 0.06, 12, 24]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.5}
          roughness={0.4}
          metalness={0.2}
        />
      </mesh>
      {/* Glow */}
      <mesh>
        <torusGeometry args={[0.34, 0.12, 8, 16]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.18}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </mesh>
      {/* N atom marker at top of ring */}
      <mesh position={[0, 0.28, 0]}>
        <sphereGeometry args={[0.08, 12, 12]} />
        <meshStandardMaterial color="#fef3c7" emissive="#fef3c7" emissiveIntensity={0.4} />
      </mesh>
    </group>
  );
}

function Bridge({
  from,
  to,
}: {
  from: [number, number, number];
  to: [number, number, number];
}) {
  const mid = new THREE.Vector3(
    (from[0] + to[0]) / 2,
    (from[1] + to[1]) / 2,
    (from[2] + to[2]) / 2,
  );
  const dir = new THREE.Vector3(
    to[0] - from[0],
    to[1] - from[1],
    to[2] - from[2],
  );
  const length = dir.length();
  const axis = new THREE.Vector3(0, 1, 0);
  const quat = new THREE.Quaternion().setFromUnitVectors(
    axis,
    dir.clone().normalize(),
  );
  return (
    <mesh position={mid} quaternion={quat}>
      <cylinderGeometry args={[0.025, 0.025, length, 8]} />
      <meshStandardMaterial color="#f5b942" emissive="#f5b942" emissiveIntensity={0.3} />
    </mesh>
  );
}
