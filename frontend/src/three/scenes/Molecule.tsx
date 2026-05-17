import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Float } from "@react-three/drei";
import * as THREE from "three";
import type { SceneProps } from "../types";
import { localProgress, lerp, smoothstep } from "../types";

/**
 * KATMAN 2/10 — Bilirubin molekülü 3D.
 *
 * Anatomically correct atomic model:
 * - 4 pirol halkası (5-membered C/N rings)
 * - 3 metenil köprü
 * - 2 propionik asit yan zinciri
 * Atoms colored by element: C dark, N blue, O red, H white.
 */
const C_COLOR = "#1f2937";
const N_COLOR = "#3b82f6";
const O_COLOR = "#dc2626";
const H_COLOR = "#f3f4f6";

const C_RAD = 0.12;
const N_RAD = 0.13;
const O_RAD = 0.13;
const H_RAD = 0.06;
const BOND_RAD = 0.04;

export function Molecule({ scroll, range }: SceneProps) {
  const groupRef = useRef<THREE.Group>(null);
  const beamRef = useRef<THREE.Mesh>(null);
  const r2Ref = useRef<THREE.Group>(null);
  const r3Ref = useRef<THREE.Group>(null);

  useFrame((state) => {
    const p = scroll.current.value;
    const lp = localProgress(p, range);
    const vis =
      smoothstep(range[0] - 0.04, range[0] + 0.02, p) *
      (1 - smoothstep(range[1] - 0.02, range[1] + 0.04, p));

    if (groupRef.current) {
      groupRef.current.visible = vis > 0.01;
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.18;
      groupRef.current.scale.setScalar(lerp(0.85, 1.15, lp));
    }
    if (beamRef.current) {
      const phase = Math.max(0, Math.min(1, (lp - 0.35) / 0.25));
      beamRef.current.position.y = lerp(3, 0.5, phase);
      const m = beamRef.current.material as THREE.MeshBasicMaterial;
      m.opacity = phase * (1 - smoothstep(0.7, 1, lp)) * vis * 0.8;
    }
    // Unfold rings 2 & 3 at mid range
    const unfold = smoothstep(0.5, 0.8, lp);
    if (r2Ref.current) {
      r2Ref.current.rotation.x = lerp(0, Math.PI, unfold);
      r2Ref.current.position.y = lerp(-0.45, 0.2, unfold);
    }
    if (r3Ref.current) {
      r3Ref.current.rotation.x = lerp(0, -Math.PI, unfold);
      r3Ref.current.position.y = lerp(0.45, -0.2, unfold);
    }
  });

  return (
    <group ref={groupRef}>
      <Float speed={1.2} rotationIntensity={0.2} floatIntensity={0.3}>
        {/* Ring 1 (left-most) */}
        <group position={[-1.4, 0, 0]}>
          <PyrroleRing />
        </group>

        {/* Ring 2 — flips with light */}
        <group ref={r2Ref} position={[-0.5, -0.45, 0]}>
          <PyrroleRing />
        </group>

        {/* Ring 3 — flips with light */}
        <group ref={r3Ref} position={[0.5, 0.45, 0]}>
          <PyrroleRing />
        </group>

        {/* Ring 4 (right-most) */}
        <group position={[1.4, 0, 0]}>
          <PyrroleRing />
        </group>

        {/* Methenyl bridges between rings */}
        <Bond from={[-1.4, 0, 0]} to={[-0.5, -0.45, 0]} />
        <Bond from={[-0.5, -0.45, 0]} to={[0.5, 0.45, 0]} double />
        <Bond from={[0.5, 0.45, 0]} to={[1.4, 0, 0]} />

        {/* Propionic acid side chains (-CH2-CH2-COOH) on rings 2 & 3 */}
        <SideChain origin={[-0.5, -0.45, 0]} direction={[0, -1, 0]} />
        <SideChain origin={[0.5, 0.45, 0]} direction={[0, 1, 0]} />

        {/* Phototherapy beam */}
        <mesh ref={beamRef} position={[0, 3, 0]}>
          <cylinderGeometry args={[0.08, 0.55, 4.5, 24, 1, true]} />
          <meshBasicMaterial
            color="#60a5fa"
            transparent
            opacity={0}
            blending={THREE.AdditiveBlending}
            depthWrite={false}
            side={THREE.DoubleSide}
          />
        </mesh>
      </Float>
    </group>
  );
}

/* ---------- Helpers ---------- */

function Atom({
  position,
  color,
  radius,
  emissive = true,
}: {
  position: [number, number, number];
  color: string;
  radius: number;
  emissive?: boolean;
}) {
  return (
    <mesh position={position}>
      <sphereGeometry args={[radius, 24, 24]} />
      <meshPhysicalMaterial
        color={color}
        emissive={emissive ? color : "#000000"}
        emissiveIntensity={emissive ? 0.4 : 0}
        roughness={0.4}
        metalness={0.1}
        clearcoat={0.6}
        clearcoatRoughness={0.3}
      />
    </mesh>
  );
}

function Bond({
  from,
  to,
  double = false,
  color = "#cbd5e1",
}: {
  from: [number, number, number];
  to: [number, number, number];
  double?: boolean;
  color?: string;
}) {
  const v = new THREE.Vector3(to[0] - from[0], to[1] - from[1], to[2] - from[2]);
  const len = v.length();
  const mid = new THREE.Vector3(
    (from[0] + to[0]) / 2,
    (from[1] + to[1]) / 2,
    (from[2] + to[2]) / 2,
  );
  const axis = new THREE.Vector3(0, 1, 0);
  const quat = new THREE.Quaternion().setFromUnitVectors(axis, v.clone().normalize());

  if (!double) {
    return (
      <mesh position={mid} quaternion={quat}>
        <cylinderGeometry args={[BOND_RAD, BOND_RAD, len, 8]} />
        <meshStandardMaterial color={color} roughness={0.4} metalness={0.05} />
      </mesh>
    );
  }
  return (
    <group position={mid} quaternion={quat}>
      <mesh position={[BOND_RAD * 1.4, 0, 0]}>
        <cylinderGeometry args={[BOND_RAD * 0.7, BOND_RAD * 0.7, len, 8]} />
        <meshStandardMaterial color={color} />
      </mesh>
      <mesh position={[-BOND_RAD * 1.4, 0, 0]}>
        <cylinderGeometry args={[BOND_RAD * 0.7, BOND_RAD * 0.7, len, 8]} />
        <meshStandardMaterial color={color} />
      </mesh>
    </group>
  );
}

function PyrroleRing() {
  // 5-membered ring: 4 C + 1 N
  // Pentagon vertices at radius 0.32
  const radius = 0.32;
  const verts: Array<[number, number, number]> = [];
  for (let i = 0; i < 5; i++) {
    const a = (i / 5) * Math.PI * 2 - Math.PI / 2;
    verts.push([Math.cos(a) * radius, Math.sin(a) * radius, 0]);
  }
  // verts[0] = top (N), 1,2 = right side (C), 3 = bottom-left (C), 4 = top-left (C)
  return (
    <group>
      <Atom position={verts[0]} color={N_COLOR} radius={N_RAD} />
      <Atom position={verts[1]} color={C_COLOR} radius={C_RAD} />
      <Atom position={verts[2]} color={C_COLOR} radius={C_RAD} />
      <Atom position={verts[3]} color={C_COLOR} radius={C_RAD} />
      <Atom position={verts[4]} color={C_COLOR} radius={C_RAD} />
      {/* Ring bonds (alternating double for aromaticity) */}
      <Bond from={verts[0]} to={verts[1]} />
      <Bond from={verts[1]} to={verts[2]} double />
      <Bond from={verts[2]} to={verts[3]} />
      <Bond from={verts[3]} to={verts[4]} double />
      <Bond from={verts[4]} to={verts[0]} />
      {/* H on N */}
      <Atom
        position={[verts[0][0] * 1.6, verts[0][1] * 1.6, 0]}
        color={H_COLOR}
        radius={H_RAD}
        emissive={false}
      />
    </group>
  );
}

function SideChain({
  origin,
  direction,
}: {
  origin: [number, number, number];
  direction: [number, number, number];
}) {
  // -CH2-CH2-COOH
  const c1: [number, number, number] = [
    origin[0] + direction[0] * 0.55,
    origin[1] + direction[1] * 0.55,
    origin[2] + direction[2] * 0.55,
  ];
  const c2: [number, number, number] = [
    origin[0] + direction[0] * 0.95,
    origin[1] + direction[1] * 0.95,
    origin[2] + direction[2] * 0.95,
  ];
  const c3: [number, number, number] = [
    origin[0] + direction[0] * 1.4,
    origin[1] + direction[1] * 1.4,
    origin[2] + direction[2] * 1.4,
  ];
  const o1: [number, number, number] = [
    c3[0] + 0.3 * direction[1],
    c3[1] - 0.3 * direction[0],
    c3[2],
  ];
  const o2: [number, number, number] = [
    c3[0] - 0.3 * direction[1],
    c3[1] + 0.3 * direction[0],
    c3[2],
  ];
  return (
    <group>
      <Atom position={c1} color={C_COLOR} radius={C_RAD} />
      <Atom position={c2} color={C_COLOR} radius={C_RAD} />
      <Atom position={c3} color={C_COLOR} radius={C_RAD} />
      <Atom position={o1} color={O_COLOR} radius={O_RAD} />
      <Atom position={o2} color={O_COLOR} radius={O_RAD} />
      <Bond from={origin} to={c1} />
      <Bond from={c1} to={c2} />
      <Bond from={c2} to={c3} />
      <Bond from={c3} to={o1} double />
      <Bond from={c3} to={o2} />
    </group>
  );
}
