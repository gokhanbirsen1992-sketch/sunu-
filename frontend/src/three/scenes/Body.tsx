import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { useGLTF, Float } from "@react-three/drei";
import * as THREE from "three";
import type { SceneProps } from "../types";
import { localProgress, lerp, smoothstep } from "../types";

// Khronos CC0 anatomical-ish humanoid figure. Loaded from /public/models/.
// Public Domain Khronos GLTF-Sample-Models.
const MODEL_PATH = `${import.meta.env.BASE_URL}models/BrainStem.glb`;

useGLTF.preload(MODEL_PATH);

/**
 * KATMAN 11 / 12.1 — Yıldız bedeni + fototerapi.
 *
 * BrainStem humanoid mesh, sarı emissive + glow halo + fototerapi
 * mavi koni. Bebek gibi küçük, etrafında parıltı.
 */
export function Body({ scroll, range }: SceneProps) {
  const { scene } = useGLTF(MODEL_PATH);
  const groupRef = useRef<THREE.Group>(null);
  const haloRef = useRef<THREE.Mesh>(null);
  const beamRef = useRef<THREE.Mesh>(null);
  const figureRef = useRef<THREE.Group>(null);

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

    const yellow = smoothstep(0, 0.4, lp) * (1 - smoothstep(0.7, 1.0, lp) * 0.4);

    if (figureRef.current) {
      figureRef.current.traverse((obj) => {
        if ((obj as THREE.Mesh).isMesh) {
          const m = (obj as THREE.Mesh).material as THREE.MeshStandardMaterial;
          if (m && "emissiveIntensity" in m) {
            m.emissive = new THREE.Color("#f5b942");
            m.emissiveIntensity = 0.3 + yellow * 0.7;
            m.color = new THREE.Color("#fef3c7");
          }
        }
      });
    }
    if (haloRef.current) {
      const m = haloRef.current.material as THREE.MeshBasicMaterial;
      m.opacity = yellow * 0.42;
      haloRef.current.scale.setScalar(1.6 + Math.sin(state.clock.elapsedTime * 1.5) * 0.05);
    }
    if (beamRef.current) {
      const photo = smoothstep(0.4, 0.7, lp);
      const m = beamRef.current.material as THREE.MeshBasicMaterial;
      m.opacity = photo * 0.55;
      beamRef.current.position.y = lerp(4.5, 1.8, photo);
    }
  });

  return (
    <group ref={groupRef} scale={2.5} position={[0, -1.2, 0]}>
      {/* Glow halo */}
      <mesh ref={haloRef} position={[0, 0.8, 0]} scale={1.6}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshBasicMaterial
          color="#f5b942"
          transparent
          opacity={0.25}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </mesh>

      {/* Humanoid figure (Khronos CC0 BrainStem) — wrapped in Float */}
      <Float speed={1.4} rotationIntensity={0.15} floatIntensity={0.25}>
        <group ref={figureRef}>
          <primitive object={scene.clone()} scale={1} />
        </group>
      </Float>

      {/* Phototherapy beam */}
      <mesh ref={beamRef} position={[0, 4.5, 0]}>
        <coneGeometry args={[1.6, 4.5, 32, 1, true]} />
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
      <lineSegments position={[0, 0.6, 0]}>
        <edgesGeometry args={[new THREE.BoxGeometry(3.2, 2.4, 1.8)]} />
        <lineBasicMaterial color="#5a3f1a" transparent opacity={0.5} />
      </lineSegments>
    </group>
  );
}
