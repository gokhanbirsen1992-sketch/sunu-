import * as THREE from 'three';
import { Room } from '../lib/room.js';
import { makeSpriteTexture } from '../lib/env.js';

export function createHero(canvas) {
  const room = new Room(canvas, {
    background: '#08060a',
    envColors: { top: '#231a16', bottom: '#02010a', horizon: '#1a1018' },
    exposure: 1.0,
    fog: { color: '#06040a', density: 0.12 },
    shadows: false,
  });

  room.camera.fov = 36;
  room.camera.updateProjectionMatrix();
  room.cameraHome.set(0, 0.1, 4.6);
  room.cameraLook.set(0, 0.0, 0);
  room.camera.position.copy(room.cameraHome);

  // Hairline gold ring (the maison's logo, abstracted).
  const ring = new THREE.Mesh(
    new THREE.TorusGeometry(1.05, 0.012, 48, 256),
    new THREE.MeshStandardMaterial({
      color: '#d9b97a',
      metalness: 1.0,
      roughness: 0.12,
      emissive: '#c9a86b',
      emissiveIntensity: 0.18,
    }),
  );
  ring.rotation.x = Math.PI / 2;
  room.scene.add(ring);

  // Inner thin ring, slightly off-axis.
  const ring2 = new THREE.Mesh(
    new THREE.TorusGeometry(0.74, 0.006, 32, 192),
    new THREE.MeshStandardMaterial({
      color: '#a88a55',
      metalness: 1.0,
      roughness: 0.35,
    }),
  );
  room.scene.add(ring2);

  // Three orbiting motes.
  const sparkTex = makeSpriteTexture();
  const motes = [];
  for (let i = 0; i < 3; i++) {
    const mat = new THREE.SpriteMaterial({
      map: sparkTex,
      color: '#ffe2b0',
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    const s = new THREE.Sprite(mat);
    s.scale.setScalar(0.45);
    s.userData.phase = Math.random() * Math.PI * 2;
    s.userData.speed = 0.4 + Math.random() * 0.4;
    s.userData.radius = 0.9 + Math.random() * 0.4;
    s.userData.tilt = (Math.random() - 0.5) * 0.7;
    motes.push(s);
    room.scene.add(s);
  }

  // Halo behind everything.
  const halo = new THREE.Mesh(
    new THREE.PlaneGeometry(6, 6),
    new THREE.MeshBasicMaterial({
      map: makeSpriteTexture([
        [0.0, 'rgba(255,220,150,0.55)'],
        [0.4, 'rgba(180,120,60,0.18)'],
        [1.0, 'rgba(0,0,0,0)'],
      ], 512),
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    }),
  );
  halo.position.z = -1.2;
  room.scene.add(halo);

  // Light kit.
  room.scene.add(new THREE.AmbientLight('#1a1320', 0.6));
  const key = new THREE.PointLight('#ffd9a3', 4.5, 8, 1.6);
  key.position.set(1.6, 0.8, 2.0);
  room.scene.add(key);
  const rim = new THREE.PointLight('#6e8aff', 1.4, 8, 1.6);
  rim.position.set(-1.8, -0.4, -0.6);
  room.scene.add(rim);

  room.update = (dt, t) => {
    ring.rotation.z = t * 0.10;
    ring2.rotation.set(Math.PI / 2 + Math.sin(t * 0.2) * 0.15, t * 0.15, 0);
    for (const m of motes) {
      const a = t * m.userData.speed + m.userData.phase;
      m.position.set(
        Math.cos(a) * m.userData.radius,
        Math.sin(a * 0.7) * m.userData.tilt,
        Math.sin(a) * m.userData.radius,
      );
      m.material.opacity = 0.65 + Math.sin(a * 2.0) * 0.3;
    }
    halo.material.opacity = 0.65 + Math.sin(t * 0.7) * 0.08;
  };

  return room;
}
