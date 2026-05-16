import * as THREE from 'three';
import { createGradientEnv } from './env.js';

// Base class for an alcove. Each room owns its own WebGL renderer, scene
// and camera. The render loop only ticks while the alcove is in view.
export class Room {
  constructor(canvas, options = {}) {
    this.canvas = canvas;
    this.options = options;
    this.visible = false;
    this.elapsed = 0;
    this.lastTime = 0;
    this.rafId = null;
    this.intensity = 0; // 0..1 entrance amount, driven by IntersectionObserver
    this.pointer = new THREE.Vector2(0, 0);
    this.pointerTarget = new THREE.Vector2(0, 0);

    this.renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: false,
      powerPreference: 'high-performance',
      preserveDrawingBuffer: false,
      stencil: false,
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = options.exposure ?? 1.0;
    this.renderer.shadowMap.enabled = options.shadows ?? true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    this.scene = new THREE.Scene();
    if (options.background !== false) {
      this.scene.background = new THREE.Color(options.background ?? '#050403');
    }
    if (options.fog) {
      this.scene.fog = new THREE.FogExp2(options.fog.color, options.fog.density);
    }

    this.camera = new THREE.PerspectiveCamera(options.fov ?? 32, 1, 0.05, 80);
    this.cameraHome = new THREE.Vector3(0, 1.1, 4.4);
    this.cameraLook = new THREE.Vector3(0, 1.05, 0);
    this.camera.position.copy(this.cameraHome);
    this.camera.lookAt(this.cameraLook);

    if (options.env !== false) {
      this.scene.environment = createGradientEnv(this.renderer, options.envColors);
    }

    this.resize = this.resize.bind(this);
    this.tick = this.tick.bind(this);
    this.onPointer = this.onPointer.bind(this);

    window.addEventListener('resize', this.resize, { passive: true });
    canvas.addEventListener('pointermove', this.onPointer, { passive: true });
    canvas.addEventListener('pointerleave', () => this.pointerTarget.set(0, 0), { passive: true });
    this.resize();
  }

  onPointer(e) {
    const rect = this.canvas.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    const y = ((e.clientY - rect.top) / rect.height) * 2 - 1;
    this.pointerTarget.set(x, -y);
  }

  resize() {
    const rect = this.canvas.getBoundingClientRect();
    const w = Math.max(2, Math.round(rect.width));
    const h = Math.max(2, Math.round(rect.height));
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
  }

  setVisible(on) {
    if (on && !this.visible) {
      this.visible = true;
      this.lastTime = performance.now();
      this.rafId = requestAnimationFrame(this.tick);
    } else if (!on && this.visible) {
      this.visible = false;
      if (this.rafId) cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
  }

  setIntensity(v) { this.intensity = v; }

  tick(now) {
    if (!this.visible) return;
    const dt = Math.min(0.05, (now - this.lastTime) / 1000);
    this.lastTime = now;
    this.elapsed += dt;

    // Smoothed parallax pointer (lazy follow).
    this.pointer.lerp(this.pointerTarget, 0.06);

    // Default subtle camera parallax around home position. Subclasses can
    // override updateCamera() if they want full control.
    if (this.updateCamera) {
      this.updateCamera(dt, this.elapsed);
    } else {
      const px = this.pointer.x * 0.18;
      const py = this.pointer.y * 0.08;
      this.camera.position.set(
        this.cameraHome.x + px,
        this.cameraHome.y + py,
        this.cameraHome.z,
      );
      this.camera.lookAt(this.cameraLook);
    }

    if (this.update) this.update(dt, this.elapsed);
    this.renderer.render(this.scene, this.camera);
    this.rafId = requestAnimationFrame(this.tick);
  }

  dispose() {
    this.setVisible(false);
    window.removeEventListener('resize', this.resize);
    this.scene.traverse((o) => {
      if (o.geometry) o.geometry.dispose();
      if (o.material) {
        const mats = Array.isArray(o.material) ? o.material : [o.material];
        for (const m of mats) m.dispose?.();
      }
    });
    if (this.scene.environment) this.scene.environment.dispose?.();
    this.renderer.dispose();
  }
}
