import { useRef } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import { PerspectiveCamera } from "@react-three/drei";
import * as THREE from "three";
import type { ScrollProgressRef } from "../hooks/useScrollProgress";
import { lerp } from "./types";

type Props = {
  scroll: ScrollProgressRef;
};

/**
 * Bir tek PerspectiveCamera. Scroll progress'iyle pozisyon, look-at ve FOV
 * sürülür. Sahneler camera'ya göre konumlanır; bu kamera ile sahnelerin
 * world position'ları arasındaki yolculuk "film çekimi" hissini verir.
 *
 * Path: kamera Z eksenine derinleşerek "atomlara" girer, "moleküle" yaklaşır,
 * sonra "hücreye" pan eder, "organa" oblique tilt yapar, en sonunda
 * geri çekilir.
 */
export function ScrollCamera({ scroll }: Props) {
  const camRef = useRef<THREE.PerspectiveCamera | null>(null);
  const set = useThree((s) => s.set);

  useFrame(() => {
    if (!camRef.current) return;
    const p = scroll.current.value;
    const cam = camRef.current;

    // Define keyframe positions in 3D space (sahneler buralarda yaşar)
    // p ∈ [0..1] linear scroll → kamera bu noktalar arasında interpolate
    const keyframes: Array<{
      pos: [number, number, number];
      lookAt: [number, number, number];
      fov: number;
      tilt: number;
    }> = [
      { pos: [0, 0, 28], lookAt: [0, 0, 0], fov: 60, tilt: 0 }, // 0.00 — uzak kozmos
      { pos: [0, 0, 12], lookAt: [0, 0, 0], fov: 55, tilt: 0 }, // 0.07 — kozmosun içinde
      { pos: [2, 0.5, 4], lookAt: [0, 0, 0], fov: 48, tilt: 0.05 }, // 0.14 — atomlara doğru
      { pos: [0, 0, 1.6], lookAt: [0, 0, 0], fov: 38, tilt: 0 }, // 0.22 — molekül
      { pos: [-0.6, 0.4, 1.0], lookAt: [0, 0, 0], fov: 36, tilt: -0.08 }, // 0.30 — ER yaklaşma
      { pos: [0, -0.5, 4.5], lookAt: [0, 0, 0], fov: 50, tilt: 0.1 }, // 0.42 — hücre geniş açı
      { pos: [3, 1, 6], lookAt: [0, 0, 0], fov: 52, tilt: 0.2 }, // 0.52 — lobül oblique
      { pos: [0, 2, 8], lookAt: [0, 0, 0], fov: 55, tilt: -0.15 }, // 0.62 — karaciğer organ
      { pos: [-2, -1, 7], lookAt: [0, 0, 0], fov: 65, tilt: 0.25 }, // 0.74 — yıldız bedeni (geniş açı oblik)
      { pos: [0, 0, 5], lookAt: [0, 0, 0], fov: 60, tilt: 0 }, // 0.86 — klinik paneller
      { pos: [0, 0, 28], lookAt: [0, 0, 0], fov: 65, tilt: 0 }, // 1.00 — geri kozmosa pullback
    ];

    const step = 1 / (keyframes.length - 1);
    const segment = Math.min(
      Math.floor(p / step),
      keyframes.length - 2,
    );
    const localT = (p - segment * step) / step;
    // Ease in-out for smoother camera moves
    const eased = localT * localT * (3 - 2 * localT);

    const a = keyframes[segment];
    const b = keyframes[segment + 1];

    cam.position.set(
      lerp(a.pos[0], b.pos[0], eased),
      lerp(a.pos[1], b.pos[1], eased),
      lerp(a.pos[2], b.pos[2], eased),
    );
    cam.lookAt(
      lerp(a.lookAt[0], b.lookAt[0], eased),
      lerp(a.lookAt[1], b.lookAt[1], eased),
      lerp(a.lookAt[2], b.lookAt[2], eased),
    );
    cam.fov = lerp(a.fov, b.fov, eased);
    cam.rotation.z = lerp(a.tilt, b.tilt, eased);
    cam.updateProjectionMatrix();
  });

  return (
    <PerspectiveCamera
      ref={(r) => {
        camRef.current = r;
        if (r) set({ camera: r });
      }}
      makeDefault
      fov={60}
      near={0.05}
      far={500}
      position={[0, 0, 28]}
    />
  );
}
