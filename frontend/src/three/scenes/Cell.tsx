import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Float, Html } from "@react-three/drei";
import * as THREE from "three";
import type { SceneProps } from "../types";
import { localProgress, lerp, smoothstep } from "../types";

/**
 * KATMAN 3 / 12.5 / 12.6 — Hepatosit.
 *
 * Hekzagonal prizma (hepatositler poligonal!) yumuşatılmış kenarlarla.
 * İçinde nucleus + ER. Sol yüzünde 2 OATP transporter, ortada UGT1A1,
 * sağ yüzünde MRP2. Bilirubin akar.
 */
export function Cell({ scroll, range }: SceneProps) {
  const groupRef = useRef<THREE.Group>(null);
  const biliRef = useRef<THREE.Mesh>(null);
  const erRef = useRef<THREE.Mesh>(null);

  // Hexagonal cell body — extruded hexagon with bevel
  const cellGeom = useMemo(() => {
    const shape = new THREE.Shape();
    const r = 1.6;
    for (let i = 0; i < 6; i++) {
      const a = (i / 6) * Math.PI * 2;
      const x = Math.cos(a) * r;
      const y = Math.sin(a) * r;
      if (i === 0) shape.moveTo(x, y);
      else shape.lineTo(x, y);
    }
    shape.closePath();
    const g = new THREE.ExtrudeGeometry(shape, {
      depth: 1.2,
      bevelEnabled: true,
      bevelThickness: 0.18,
      bevelSize: 0.18,
      bevelSegments: 5,
      curveSegments: 32,
    });
    g.translate(0, 0, -0.6);
    return g;
  }, []);

  // Nucleus — bumpy sphere
  const nucleusGeom = useMemo(() => {
    const g = new THREE.IcosahedronGeometry(0.42, 4);
    const pos = g.attributes.position as THREE.BufferAttribute;
    const v = new THREE.Vector3();
    let s = 17;
    const rand = () => {
      s = (s * 9301 + 49297) % 233280;
      return s / 233280 - 0.5;
    };
    for (let i = 0; i < pos.count; i++) {
      v.fromBufferAttribute(pos, i);
      v.multiplyScalar(1 + rand() * 0.08);
      pos.setXYZ(i, v.x, v.y, v.z);
    }
    g.computeVertexNormals();
    return g;
  }, []);

  useFrame((state) => {
    const p = scroll.current.value;
    const lp = localProgress(p, range);
    const vis =
      smoothstep(range[0] - 0.04, range[0] + 0.02, p) *
      (1 - smoothstep(range[1] - 0.02, range[1] + 0.04, p));

    if (groupRef.current) {
      groupRef.current.visible = vis > 0.01;
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.1 + lp * 0.3;
      groupRef.current.rotation.x = lerp(0.1, -0.05, lp);
    }
    if (biliRef.current) {
      biliRef.current.position.x = lerp(-2.0, 2.0, lp);
      biliRef.current.position.y = Math.sin(lp * Math.PI) * 0.25;
      const m = biliRef.current.material as THREE.MeshStandardMaterial;
      m.color.set(lp > 0.5 ? "#7dd3fc" : "#f5b942");
      m.emissive.set(lp > 0.5 ? "#7dd3fc" : "#f5b942");
    }
    if (erRef.current) {
      const erPulse = smoothstep(0.3, 0.5, lp) * (1 - smoothstep(0.65, 0.85, lp));
      erRef.current.scale.setScalar(
        0.95 + erPulse * 0.15 + Math.sin(state.clock.elapsedTime * 3) * 0.03 * erPulse,
      );
    }
  });

  return (
    <group ref={groupRef}>
      <Float speed={0.9} rotationIntensity={0.1} floatIntensity={0.15}>
        {/* Hexagonal hepatocyte body */}
        <mesh geometry={cellGeom} rotation={[0, 0, 0]}>
          <meshPhysicalMaterial
            color="#5b4a78"
            transparent
            opacity={0.32}
            roughness={0.55}
            metalness={0.0}
            transmission={0.4}
            thickness={0.6}
            ior={1.4}
            clearcoat={0.5}
            clearcoatRoughness={0.3}
            attenuationColor="#9988bb"
            attenuationDistance={2}
            side={THREE.DoubleSide}
          />
        </mesh>

        {/* Membrane wireframe overlay */}
        <mesh geometry={cellGeom}>
          <meshBasicMaterial color="#a78bfa" wireframe transparent opacity={0.18} />
        </mesh>

        {/* Nucleus */}
        <mesh geometry={nucleusGeom} position={[-0.3, 0.2, 0]}>
          <meshPhysicalMaterial
            color="#332a55"
            roughness={0.5}
            clearcoat={0.7}
            emissive="#221a44"
            emissiveIntensity={0.4}
          />
        </mesh>

        {/* ER — UGT1A1 (small organelle near nucleus) */}
        <mesh ref={erRef} position={[0.3, -0.1, 0]}>
          <torusKnotGeometry args={[0.25, 0.07, 64, 16, 2, 3]} />
          <meshPhysicalMaterial
            color="#c084fc"
            emissive="#c084fc"
            emissiveIntensity={0.7}
            roughness={0.35}
            metalness={0.1}
            clearcoat={0.5}
          />
        </mesh>

        {/* Basolateral gates (left side) — OATP1B1/B3 */}
        <group position={[-1.55, 0, 0]}>
          <mesh position={[0, 0.6, 0]} rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry args={[0.14, 0.14, 0.5, 12]} />
            <meshStandardMaterial
              color="#34d399"
              emissive="#34d399"
              emissiveIntensity={0.6}
              roughness={0.4}
            />
          </mesh>
          <mesh position={[0, -0.6, 0]} rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry args={[0.14, 0.14, 0.5, 12]} />
            <meshStandardMaterial
              color="#34d399"
              emissive="#34d399"
              emissiveIntensity={0.6}
              roughness={0.4}
            />
          </mesh>
          <Html position={[-0.4, 1.5, 0]} center transform={false} style={{ pointerEvents: "none" }}>
            <div style={labelStyle("#34d399")}>OATP1B1/B3</div>
          </Html>
        </group>

        {/* Apical gate (right) — MRP2 */}
        <group position={[1.55, 0, 0]}>
          <mesh rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry args={[0.18, 0.18, 0.55, 12]} />
            <meshStandardMaterial
              color="#84cc16"
              emissive="#84cc16"
              emissiveIntensity={0.65}
              roughness={0.4}
            />
          </mesh>
          <Html position={[0.4, 1.0, 0]} center transform={false} style={{ pointerEvents: "none" }}>
            <div style={labelStyle("#84cc16")}>MRP2</div>
          </Html>
        </group>

        {/* UGT1A1 label */}
        <Html position={[0.3, -0.7, 0]} center transform={false} style={{ pointerEvents: "none" }}>
          <div style={labelStyle("#c084fc")}>UGT1A1</div>
        </Html>

        {/* Traveling bilirubin */}
        <mesh ref={biliRef} position={[-2.0, 0, 0]}>
          <sphereGeometry args={[0.15, 24, 24]} />
          <meshStandardMaterial
            color="#f5b942"
            emissive="#f5b942"
            emissiveIntensity={0.8}
            roughness={0.3}
          />
        </mesh>
      </Float>
    </group>
  );
}

function labelStyle(color: string): React.CSSProperties {
  return {
    fontFamily: "Inter, sans-serif",
    fontSize: 10,
    letterSpacing: "0.18em",
    color,
    fontWeight: 600,
    textTransform: "uppercase",
    background: "rgba(10, 9, 7, 0.6)",
    padding: "3px 8px",
    borderRadius: 4,
    border: `1px solid ${color}55`,
    whiteSpace: "nowrap",
  };
}
