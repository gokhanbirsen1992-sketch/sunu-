import * as THREE from 'three';

// Procedural environment map. Builds a tiny gradient scene and bakes it
// through PMREMGenerator so PBR materials have something to reflect.
// No external HDRI required.

export function createGradientEnv(renderer, { top = '#1a1614', bottom = '#050403', horizon = null } = {}) {
  const pmrem = new THREE.PMREMGenerator(renderer);
  pmrem.compileEquirectangularShader();

  const scene = new THREE.Scene();

  const uniforms = {
    cTop:    { value: new THREE.Color(top) },
    cBottom: { value: new THREE.Color(bottom) },
    cMid:    { value: new THREE.Color(horizon ?? blend(top, bottom, 0.5)) },
  };

  const mat = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    uniforms,
    vertexShader: /* glsl */`
      varying vec3 vDir;
      void main() {
        vDir = normalize(position);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: /* glsl */`
      varying vec3 vDir;
      uniform vec3 cTop;
      uniform vec3 cMid;
      uniform vec3 cBottom;
      void main() {
        float h = vDir.y * 0.5 + 0.5;
        vec3 col = mix(cBottom, cMid, smoothstep(0.0, 0.55, h));
        col = mix(col, cTop, smoothstep(0.45, 1.0, h));
        gl_FragColor = vec4(col, 1.0);
      }
    `,
  });

  const sphere = new THREE.Mesh(new THREE.SphereGeometry(50, 32, 24), mat);
  scene.add(sphere);

  const target = pmrem.fromScene(scene, 0.04);
  sphere.geometry.dispose();
  mat.dispose();
  pmrem.dispose();
  return target.texture;
}

function blend(a, b, t) {
  const ca = new THREE.Color(a);
  const cb = new THREE.Color(b);
  return ca.lerp(cb, t).getStyle();
}

// Radial sprite texture, useful for halos, particles, bokeh.
export function makeSpriteTexture(stops = [
  [0.0, 'rgba(255, 230, 180, 1)'],
  [0.4, 'rgba(255, 200, 130, 0.4)'],
  [1.0, 'rgba(0, 0, 0, 0)'],
], size = 256) {
  const cnv = document.createElement('canvas');
  cnv.width = cnv.height = size;
  const ctx = cnv.getContext('2d');
  const g = ctx.createRadialGradient(size/2, size/2, 0, size/2, size/2, size/2);
  for (const [s, c] of stops) g.addColorStop(s, c);
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  const tex = new THREE.CanvasTexture(cnv);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 4;
  return tex;
}
