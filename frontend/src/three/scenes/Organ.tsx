import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Float } from "@react-three/drei";
import * as THREE from "three";
import type { SceneProps } from "../types";
import { localProgress, lerp, smoothstep } from "../types";

/**
 * KATMAN 5 / 7 / 9 — Karaciğer.
 *
 * Anatomik olarak şekillendirilmiş 4-lobed liver: büyük sağ lob,
 * küçük sol lob, kaudat ve kuadrat. Her lob displacement'lı bir
 * deforme ellipsoid. Yumuşak doku rengi + clearcoat.
 */
export function Organ({ scroll, range }: SceneProps) {
  const groupRef = useRef<THREE.Group>(null);
  const liverRef = useRef<THREE.Group>(null);

  // Pre-compute displaced geometries for an organic, lobed look
  const geometries = useMemo(() => {
    const make = (radius: number, displaceAmount: number, seed: number) => {
      const g = new THREE.IcosahedronGeometry(radius, 6);
      const pos = g.attributes.position as THREE.BufferAttribute;
      const v = new THREE.Vector3();
      let s = seed;
      const rand = () => {
        s = (s * 9301 + 49297) % 233280;
        return s / 233280 - 0.5;
      };
      for (let i = 0; i < pos.count; i++) {
        v.fromBufferAttribute(pos, i);
        const d = 1 + rand() * displaceAmount + Math.sin(v.x * 3 + v.y * 2) * displaceAmount * 0.5;
        v.multiplyScalar(d);
        pos.setXYZ(i, v.x, v.y, v.z);
      }
      g.computeVertexNormals();
      return g;
    };
    return {
      rightLobe: make(1.4, 0.15, 11),
      leftLobe: make(0.8, 0.18, 23),
      caudate: make(0.35, 0.2, 47),
      quadrate: make(0.4, 0.18, 71),
    };
  }, []);

  useFrame((state) => {
    const p = scroll.current.value;
    const lp = localProgress(p, range);
    const vis =
      smoothstep(range[0] - 0.04, range[0] + 0.02, p) *
      (1 - smoothstep(range[1] - 0.02, range[1] + 0.04, p));

    if (groupRef.current) {
      groupRef.current.visible = vis > 0.01;
      groupRef.current.rotation.y =
        state.clock.elapsedTime * 0.08 + lp * 0.4;
      groupRef.current.rotation.x = lerp(0.2, -0.05, lp);
    }
    if (liverRef.current) {
      const grow = smoothstep(0, 0.3, lp);
      liverRef.current.scale.setScalar(0.7 + grow * 0.5);
    }
  });

  return (
    <group ref={groupRef}>
      <Float speed={1.0} rotationIntensity={0.1} floatIntensity={0.18}>
        <group ref={liverRef}>
          {/* Right lobe — largest */}
          <mesh
            geometry={geometries.rightLobe}
            position={[0.4, 0, 0]}
            rotation={[0, 0.2, -0.1]}
            scale={[1.2, 0.85, 0.95]}
          >
            <meshPhysicalMaterial
              color="#7a2d22"
              roughness={0.55}
              metalness={0.0}
              clearcoat={0.7}
              clearcoatRoughness={0.4}
              sheen={0.5}
              sheenColor="#f97316"
              emissive="#3d1108"
              emissiveIntensity={0.4}
            />
          </mesh>
          {/* Left lobe */}
          <mesh
            geometry={geometries.leftLobe}
            position={[-1.1, 0.15, 0.05]}
            scale={[1.0, 0.7, 0.85]}
          >
            <meshPhysicalMaterial
              color="#7a2d22"
              roughness={0.55}
              clearcoat={0.7}
              clearcoatRoughness={0.4}
              emissive="#3d1108"
              emissiveIntensity={0.4}
            />
          </mesh>
          {/* Caudate lobe (top behind) */}
          <mesh
            geometry={geometries.caudate}
            position={[-0.2, 0.5, -0.4]}
            scale={[0.9, 0.8, 0.7]}
          >
            <meshPhysicalMaterial
              color="#702820"
              roughness={0.6}
              clearcoat={0.5}
              emissive="#3d1108"
              emissiveIntensity={0.35}
            />
          </mesh>
          {/* Quadrate lobe */}
          <mesh
            geometry={geometries.quadrate}
            position={[-0.1, -0.4, 0.3]}
            scale={[0.85, 0.6, 0.75]}
          >
            <meshPhysicalMaterial
              color="#702820"
              roughness={0.6}
              clearcoat={0.55}
              emissive="#3d1108"
              emissiveIntensity={0.35}
            />
          </mesh>
          {/* Gallbladder hint */}
          <mesh position={[0.05, -0.55, 0.7]} scale={[0.18, 0.3, 0.18]}>
            <sphereGeometry args={[1, 16, 16]} />
            <meshPhysicalMaterial
              color="#3b3b1f"
              roughness={0.3}
              clearcoat={0.9}
              emissive="#2d2d1a"
              emissiveIntensity={0.5}
            />
          </mesh>
        </group>
      </Float>
    </group>
  );
}
