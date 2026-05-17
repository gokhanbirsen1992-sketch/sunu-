import { useEffect, useRef } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import type { ScrollProgressRef } from "../hooks/useScrollProgress";
import { lerp } from "./types";

type Props = {
  scroll: ScrollProgressRef;
};

/**
 * Default kamerayı doğrudan kontrol eder. Scroll progress kamera
 * pozisyonu, lookAt ve FOV'unu 10 keyframe arasında interpolate eder.
 */
export function ScrollCamera({ scroll }: Props) {
  const camera = useThree((s) => s.camera) as THREE.PerspectiveCamera;
  const lookAtVec = useRef(new THREE.Vector3());

  // Set initial state immediately so first frame isn't black
  useEffect(() => {
    camera.position.set(0, 0, 28);
    camera.lookAt(0, 0, 0);
    if ("fov" in camera) {
      camera.fov = 60;
      camera.updateProjectionMatrix();
    }
  }, [camera]);

  useFrame(() => {
    const p = scroll.current.value;

    const keyframes: Array<{
      pos: [number, number, number];
      lookAt: [number, number, number];
      fov: number;
      tilt: number;
    }> = [
      { pos: [0, 0, 28], lookAt: [0, 0, 0], fov: 60, tilt: 0 },
      { pos: [0, 0, 12], lookAt: [0, 0, 0], fov: 55, tilt: 0 },
      { pos: [2, 0.5, 4], lookAt: [0, 0, 0], fov: 48, tilt: 0.05 },
      { pos: [0, 0, 1.6], lookAt: [0, 0, 0], fov: 38, tilt: 0 },
      { pos: [-0.6, 0.4, 1.0], lookAt: [0, 0, 0], fov: 36, tilt: -0.08 },
      { pos: [0, -0.5, 4.5], lookAt: [0, 0, 0], fov: 50, tilt: 0.1 },
      { pos: [3, 1, 6], lookAt: [0, 0, 0], fov: 52, tilt: 0.2 },
      { pos: [0, 2, 8], lookAt: [0, 0, 0], fov: 55, tilt: -0.15 },
      { pos: [-2, -1, 7], lookAt: [0, 0, 0], fov: 65, tilt: 0.25 },
      { pos: [0, 0, 5], lookAt: [0, 0, 0], fov: 60, tilt: 0 },
      { pos: [0, 0, 28], lookAt: [0, 0, 0], fov: 65, tilt: 0 },
    ];

    const step = 1 / (keyframes.length - 1);
    const segment = Math.min(
      Math.floor(p / step),
      keyframes.length - 2,
    );
    const localT = (p - segment * step) / step;
    const eased = localT * localT * (3 - 2 * localT);

    const a = keyframes[segment];
    const b = keyframes[segment + 1];

    camera.position.set(
      lerp(a.pos[0], b.pos[0], eased),
      lerp(a.pos[1], b.pos[1], eased),
      lerp(a.pos[2], b.pos[2], eased),
    );
    lookAtVec.current.set(
      lerp(a.lookAt[0], b.lookAt[0], eased),
      lerp(a.lookAt[1], b.lookAt[1], eased),
      lerp(a.lookAt[2], b.lookAt[2], eased),
    );
    camera.lookAt(lookAtVec.current);
    if ("fov" in camera) {
      camera.fov = lerp(a.fov, b.fov, eased);
      camera.rotation.z = lerp(a.tilt, b.tilt, eased);
      camera.updateProjectionMatrix();
    }
  });

  return null;
}
