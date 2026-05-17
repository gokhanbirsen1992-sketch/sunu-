import {
  Bloom,
  ChromaticAberration,
  EffectComposer,
  Noise,
  Vignette,
} from "@react-three/postprocessing";
import { BlendFunction } from "postprocessing";
import { Vector2 } from "three";

/**
 * Sinema lens hissi için post-processing pipeline.
 * - Bloom: parlayan elementlere gerçek "ışıma"
 * - ChromaticAberration: lens distorsiyonu hissi
 * - Vignette: kenarları yumuşak karart
 * - Noise: film grain (subtle)
 */
export function Effects() {
  return (
    <EffectComposer multisampling={4} enableNormalPass={false}>
      <Bloom
        intensity={0.85}
        luminanceThreshold={0.2}
        luminanceSmoothing={0.4}
        mipmapBlur
      />
      <ChromaticAberration
        offset={new Vector2(0.0008, 0.0008)}
        radialModulation={false}
        modulationOffset={0}
      />
      <Vignette eskil={false} offset={0.32} darkness={0.7} />
      <Noise opacity={0.05} blendFunction={BlendFunction.OVERLAY} />
    </EffectComposer>
  );
}
