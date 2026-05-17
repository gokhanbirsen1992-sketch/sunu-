import { Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import { Environment, ContactShadows } from "@react-three/drei";
import type { ScrollProgressRef } from "../hooks/useScrollProgress";
import { ScrollCamera } from "./ScrollCamera";
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

export function Stage({ scroll }: Props) {
  return (
    <div className="stage">
      <Canvas
        dpr={[1, 2]}
        gl={{
          antialias: true,
          alpha: true,
          powerPreference: "high-performance",
          preserveDrawingBuffer: false,
        }}
        camera={{ position: [0, 0, 28], fov: 60, near: 0.05, far: 500 }}
        onCreated={({ gl }) => {
          gl.setClearColor(0x03040a, 0);
        }}
      >
        <Suspense fallback={null}>
          <ScrollCamera scroll={scroll} />

          {/* IBL lighting via drei Environment — instant quality jump */}
          <Environment preset="night" environmentIntensity={0.6} />

          {/* Direct lights to complement IBL */}
          <ambientLight intensity={0.3} color="#9fa5b8" />
          <directionalLight position={[5, 6, 5]} intensity={1.2} color="#fef3c7" castShadow />
          <directionalLight position={[-5, -3, 2]} intensity={0.45} color="#a78bfa" />
          <hemisphereLight args={["#fde68a", "#1a1224", 0.4]} />

          <Cosmos scroll={scroll} range={[0.0, 0.16]} />
          <Atoms scroll={scroll} range={[0.1, 0.22]} />
          <Molecule scroll={scroll} range={[0.18, 0.34]} />
          <Cell scroll={scroll} range={[0.3, 0.55]} />
          <Organ scroll={scroll} range={[0.52, 0.72]} />
          <Body scroll={scroll} range={[0.68, 0.9]} />
          <Pullback scroll={scroll} range={[0.85, 1.0]} />

          <ContactShadows
            position={[0, -3.5, 0]}
            opacity={0.35}
            blur={2.5}
            scale={20}
            far={5}
            color="#000000"
          />
        </Suspense>
      </Canvas>
    </div>
  );
}
