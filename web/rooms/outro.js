import * as THREE from 'three';
import { Room } from '../lib/room.js';
import { makeSpriteTexture } from '../lib/env.js';

// Outro — a slow closing curtain of light.
export function createOutro(canvas) {
  const room = new Room(canvas, {
    background: '#06040a',
    envColors: { top: '#15101a', bottom: '#02010a' },
    exposure: 0.95,
    shadows: false,
  });
  room.cameraHome.set(0, 0, 4);
  room.cameraLook.set(0, 0, 0);
  room.camera.position.copy(room.cameraHome);

  // Slow vertical bar of light — the cabinet door closing.
  const bar = new THREE.Mesh(
    new THREE.PlaneGeometry(0.04, 4),
    new THREE.MeshBasicMaterial({ color: '#e8c98a', transparent: true, opacity: 0.85 }),
  );
  room.scene.add(bar);

  const glow = new THREE.Mesh(
    new THREE.PlaneGeometry(2.4, 4),
    new THREE.MeshBasicMaterial({
      map: makeSpriteTexture([
        [0.0, 'rgba(255,210,140,0.85)'],
        [0.45,'rgba(180,100,40,0.18)'],
        [1.0, 'rgba(0,0,0,0)'],
      ], 256),
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    }),
  );
  glow.position.z = -0.1;
  room.scene.add(glow);

  // Slow drifting motes.
  const motes = [];
  const moteTex = makeSpriteTexture();
  for (let i = 0; i < 20; i++) {
    const m = new THREE.Sprite(new THREE.SpriteMaterial({
      map: moteTex,
      color: '#ffe2b0',
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    }));
    m.scale.setScalar(0.08 + Math.random() * 0.10);
    m.position.set(
      (Math.random() - 0.5) * 4,
      (Math.random() - 0.5) * 3,
      -0.5 - Math.random() * 1.5,
    );
    m.userData.driftY = 0.05 + Math.random() * 0.1;
    m.userData.phase = Math.random() * Math.PI * 2;
    motes.push(m);
    room.scene.add(m);
  }

  room.scene.add(new THREE.AmbientLight('#1a1320', 0.4));

  room.update = (dt, t) => {
    // The bar pulses gently and the glow breathes.
    bar.material.opacity = 0.7 + Math.sin(t * 0.6) * 0.15;
    glow.material.opacity = 0.65 + Math.sin(t * 0.4) * 0.10;
    glow.scale.x = 1.0 + Math.sin(t * 0.25) * 0.08;
    for (const m of motes) {
      m.position.y += dt * m.userData.driftY;
      m.position.x += Math.sin(t * 0.4 + m.userData.phase) * dt * 0.02;
      if (m.position.y > 1.8) m.position.y = -1.8;
      m.material.opacity = 0.4 + (Math.sin(t * 0.8 + m.userData.phase) + 1) / 2 * 0.5;
    }
  };

  return room;
}
