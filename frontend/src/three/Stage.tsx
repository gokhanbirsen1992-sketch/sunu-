import { Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import type { ScrollProgressRef } from "../hooks/useScrollProgress";
import { ScrollCamera } from "./ScrollCamera";
import { Effects } from "./Effects";
import { Cosmos } from "./scenes/Cosmos";
import { Atoms } from "./scenes/Atoms";
import { Molecule } from "./scenes/Molecule";
import { Cell } from "./scenes/Cell";
import { Organ } from "./scenes/Organ";
import { Body } from "./scenes/Body";
import { Pullback } from "./scenes/Pullback";

type Props = {
  scroll: ScrollProgressRef;
};

/**
 * R3F kök sahnesi. Sticky bir wrapper içinde tüm 3D sahneler yaşar.
 * ScrollCamera scroll progress'iyle kamera pozisyonunu sürer; her
 * sahne kendi range'inde aktive olur.
 *
 * Sahne range'leri kameranın koreografisiyle eşleştirilmiş:
 *   [0.00, 0.16] — Cosmos (kozmos + atomlar)
 *   [0.10, 0.22] — Atoms (overlay, geçiş)
 *   [0.18, 0.32] — Molecule (bilirubin)
 *   [0.32, 0.55] — Cell (hepatosit)
 *   [0.52, 0.72] — Organ (karaciğer)
 *   [0.68, 0.88] — Body (Yıldız + inkübatör)
 *   [0.85, 1.00] — Pullback (kapanış)
 */
export function Stage({ scroll }: Props) {
  return (
    <div className="stage">
      <Canvas
        dpr={[1, 2]}
        gl={{
          antialias: true,
          alpha: true,
          powerPreference: "high-performance",
        }}
        camera={{ position: [0, 0, 28], fov: 60 }}
      >
        <Suspense fallback={null}>
          <ScrollCamera scroll={scroll} />

          {/* Ambient + directional lights */}
          <ambientLight intensity={0.45} color="#9fa5b8" />
          <directionalLight position={[5, 6, 5]} intensity={1.1} color="#fef3c7" />
          <directionalLight position={[-5, -3, 2]} intensity={0.45} color="#a78bfa" />

          {/* Scenes */}
          <Cosmos scroll={scroll} range={[0.0, 0.16]} />
          <Atoms scroll={scroll} range={[0.1, 0.22]} />
          <Molecule scroll={scroll} range={[0.18, 0.34]} />
          <Cell scroll={scroll} range={[0.3, 0.55]} />
          <Organ scroll={scroll} range={[0.52, 0.72]} />
          <Body scroll={scroll} range={[0.68, 0.9]} />
          <Pullback scroll={scroll} range={[0.85, 1.0]} />

          <Effects />
        </Suspense>
      </Canvas>
    </div>
  );
}
