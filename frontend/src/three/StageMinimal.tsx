import { Canvas } from "@react-three/fiber";

/** Minimal R3F test: just a rotating cube. No framer-motion, no drei. */
export function StageMinimal() {
  return (
    <div className="stage">
      <Canvas
        dpr={[1, 2]}
        camera={{ position: [0, 0, 5], fov: 60 }}
        gl={{ antialias: true, alpha: true }}
      >
        <ambientLight intensity={0.5} />
        <directionalLight position={[2, 2, 2]} intensity={1} />
        <mesh rotation={[0.5, 0.5, 0]}>
          <boxGeometry args={[1, 1, 1]} />
          <meshStandardMaterial color="#f5b942" />
        </mesh>
      </Canvas>
    </div>
  );
}
