import * as THREE from 'three';
import { Room } from '../lib/room.js';

// Onyx — three obsidian shards on brushed gunmetal, cold blue beam.
export function createOnyx(canvas) {
  const room = new Room(canvas, {
    background: '#04060a',
    envColors: { top: '#0c1828', bottom: '#020308', horizon: '#0f2238' },
    exposure: 0.85,
    fog: { color: '#03060a', density: 0.18 },
  });
  room.cameraHome.set(0.4, 1.0, 3.6);
  room.cameraLook.set(0.0, 0.85, 0.0);
  room.camera.position.copy(room.cameraHome);

  // Floor — slick brushed gunmetal.
  const floor = new THREE.Mesh(
    new THREE.CircleGeometry(6, 64),
    new THREE.MeshPhysicalMaterial({
      color: '#0f1116',
      metalness: 0.8,
      roughness: 0.35,
      clearcoat: 0.6,
      clearcoatRoughness: 0.4,
    }),
  );
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  room.scene.add(floor);

  // Cluster of three shards.
  const shardMat = new THREE.MeshPhysicalMaterial({
    color: '#0a0a10',
    metalness: 0.3,
    roughness: 0.05,
    clearcoat: 1.0,
    clearcoatRoughness: 0.05,
    reflectivity: 0.4,
  });

  const cluster = new THREE.Group();
  const params = [
    { h: 1.4, w: 0.16, tilt:  0.12, rot:  0.0, x: 0.00, z:  0.00 },
    { h: 1.05, w: 0.13, tilt: -0.20, rot:  1.4, x: -0.32, z:  0.20 },
    { h: 0.85, w: 0.11, tilt:  0.22, rot: -1.1, x:  0.30, z:  0.18 },
  ];
  for (const p of params) {
    const geom = new THREE.ConeGeometry(p.w, p.h, 6, 1);
    // Compress to make it less symmetrical.
    geom.scale(1.0, 1.0, 0.55);
    const m = new THREE.Mesh(geom, shardMat);
    m.position.set(p.x, p.h / 2, p.z);
    m.rotation.set(p.tilt, p.rot, p.tilt * 0.4);
    m.castShadow = true;
    cluster.add(m);
  }
  room.scene.add(cluster);

  // Faint dust particles caught in the beam.
  const dust = makeDust(140);
  room.scene.add(dust);

  // Lights.
  room.scene.add(new THREE.AmbientLight('#08101c', 0.4));

  const beam = new THREE.SpotLight('#7fb4ff', 14, 8, Math.PI / 9, 0.5, 1.2);
  beam.position.set(0.0, 4.5, 0.5);
  beam.target.position.set(0.0, 0.6, 0.0);
  beam.castShadow = true;
  beam.shadow.mapSize.set(1024, 1024);
  beam.shadow.bias = -0.0005;
  room.scene.add(beam, beam.target);

  const rim = new THREE.PointLight('#3a6dff', 1.4, 5, 1.8);
  rim.position.set(-1.6, 1.2, -1.0);
  room.scene.add(rim);

  const warm = new THREE.PointLight('#a96a3a', 0.5, 4, 2);
  warm.position.set(2.0, 0.4, 1.0);
  room.scene.add(warm);

  room.update = (dt, t) => {
    cluster.rotation.y = Math.sin(t * 0.18) * 0.35 + t * 0.04;
    // Slow flicker of the beam.
    beam.intensity = 13 + Math.sin(t * 1.7) * 0.6 + Math.sin(t * 0.7) * 0.4;
    // Drift dust.
    const pos = dust.geometry.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      let y = pos.getY(i);
      y += dt * (0.05 + (i % 3) * 0.02);
      if (y > 3.0) y = -0.1;
      pos.setY(i, y);
    }
    pos.needsUpdate = true;
  };

  return room;
}

function makeDust(n) {
  const geom = new THREE.BufferGeometry();
  const pos = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) {
    pos[i * 3 + 0] = (Math.random() - 0.5) * 1.2;
    pos[i * 3 + 1] = Math.random() * 3.0;
    pos[i * 3 + 2] = (Math.random() - 0.5) * 1.2;
  }
  geom.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const mat = new THREE.PointsMaterial({
    color: '#bcd1ff',
    size: 0.012,
    transparent: true,
    opacity: 0.6,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    sizeAttenuation: true,
  });
  return new THREE.Points(geom, mat);
}
