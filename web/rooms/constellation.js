import * as THREE from 'three';
import { Room } from '../lib/room.js';
import { makeSpriteTexture } from '../lib/env.js';

// Constellation — a platinum circle of diamonds beneath a starfield.
export function createConstellation(canvas) {
  const room = new Room(canvas, {
    background: '#020308',
    envColors: { top: '#0a0e1a', bottom: '#01020a', horizon: '#0a1330' },
    exposure: 1.0,
    fog: { color: '#01020a', density: 0.08 },
  });
  room.cameraHome.set(0.3, 0.9, 3.2);
  room.cameraLook.set(0.0, 0.85, 0.0);
  room.camera.position.copy(room.cameraHome);

  // Backdrop — large sphere with star sprites inside (we render points instead).
  const stars = makeStarfield(420);
  stars.position.z = -4;
  room.scene.add(stars);

  // Pedestal.
  const ped = new THREE.Mesh(
    new THREE.CylinderGeometry(0.9, 1.05, 0.14, 64),
    new THREE.MeshStandardMaterial({ color: '#0b0c14', roughness: 0.6, metalness: 0.4 }),
  );
  ped.position.y = 0.07;
  ped.receiveShadow = true;
  room.scene.add(ped);

  // Platinum circle.
  const platinum = new THREE.MeshPhysicalMaterial({
    color: '#dde2ea',
    metalness: 1.0,
    roughness: 0.18,
    clearcoat: 0.7,
    clearcoatRoughness: 0.1,
  });

  const necklace = new THREE.Group();
  necklace.position.set(0, 0.95, 0);
  room.scene.add(necklace);

  const ring = new THREE.Mesh(
    new THREE.TorusGeometry(0.7, 0.013, 24, 220),
    platinum,
  );
  ring.rotation.x = Math.PI / 2.2;
  ring.castShadow = true;
  necklace.add(ring);

  // 21 settings around the ring.
  const stoneMat = new THREE.MeshPhysicalMaterial({
    color: '#ffffff',
    metalness: 0.0,
    roughness: 0.03,
    transmission: 1.0,
    thickness: 0.2,
    ior: 2.4,
    attenuationColor: '#eaf2ff',
    attenuationDistance: 0.3,
    envMapIntensity: 1.4,
  });
  const settingMat = platinum;

  const N = 21;
  const a0 = -Math.PI / 2;
  for (let i = 0; i < N; i++) {
    const a = a0 + (i / N) * Math.PI * 2;
    const big = i === 0; // pendant at the bottom of the arc (front-most)
    const r = 0.7;
    // place around the tilted ring's plane
    const local = new THREE.Vector3(Math.cos(a) * r, 0, Math.sin(a) * r);
    local.applyEuler(new THREE.Euler(Math.PI / 2.2, 0, 0));
    const setting = new THREE.Mesh(
      new THREE.CylinderGeometry(big ? 0.022 : 0.015, big ? 0.030 : 0.020, 0.018, 16),
      settingMat,
    );
    setting.position.copy(local);
    setting.castShadow = true;
    necklace.add(setting);

    const stone = new THREE.Mesh(
      new THREE.OctahedronGeometry(big ? 0.05 : 0.028, 0),
      stoneMat,
    );
    stone.position.copy(local).add(new THREE.Vector3(0, 0.022, 0));
    stone.castShadow = true;
    necklace.add(stone);
  }

  // Glints — additive sprites that pop near each stone.
  const glintTex = makeSpriteTexture([
    [0.0, 'rgba(255,255,255,1)'],
    [0.2, 'rgba(200,220,255,0.6)'],
    [1.0, 'rgba(0,0,0,0)'],
  ], 128);
  const glints = [];
  for (let i = 0; i < 21; i++) {
    const s = new THREE.Sprite(new THREE.SpriteMaterial({
      map: glintTex, color: '#ffffff', transparent: true,
      depthWrite: false, blending: THREE.AdditiveBlending,
    }));
    s.scale.setScalar(0.18);
    s.userData.phase = Math.random() * Math.PI * 2;
    s.userData.speed = 0.6 + Math.random() * 0.6;
    necklace.add(s);
    glints.push({ sprite: s, index: i });
  }

  // Lights.
  room.scene.add(new THREE.AmbientLight('#0a0f1c', 0.55));

  const moon = new THREE.DirectionalLight('#cfd9ff', 1.8);
  moon.position.set(0.8, 3.2, 1.6);
  moon.castShadow = true;
  moon.shadow.mapSize.set(1024, 1024);
  moon.shadow.bias = -0.0006;
  room.scene.add(moon);

  const warm = new THREE.PointLight('#ffb878', 0.6, 4, 2);
  warm.position.set(-1.2, 0.6, 1.0);
  room.scene.add(warm);

  const accent = new THREE.PointLight('#90b5ff', 1.4, 4, 1.8);
  accent.position.set(1.2, 1.5, 0.6);
  room.scene.add(accent);

  room.update = (dt, t) => {
    necklace.rotation.y = t * 0.10;
    // Glints rotate around the ring and pulse.
    for (let i = 0; i < glints.length; i++) {
      const g = glints[i];
      const a = (i / glints.length) * Math.PI * 2 + t * 0.4 + g.sprite.userData.phase;
      const v = new THREE.Vector3(Math.cos(a) * 0.71, 0, Math.sin(a) * 0.71);
      v.applyEuler(new THREE.Euler(Math.PI / 2.2, 0, 0));
      g.sprite.position.copy(v).add(new THREE.Vector3(0, 0.025, 0));
      const pulse = (Math.sin(t * g.sprite.userData.speed + g.sprite.userData.phase) + 1) / 2;
      g.sprite.material.opacity = 0.15 + pulse * pulse * 0.85;
      g.sprite.scale.setScalar(0.13 + pulse * 0.10);
    }
    // Slow drift of stars.
    stars.rotation.z = t * 0.01;
  };

  return room;
}

function makeStarfield(n) {
  const geom = new THREE.BufferGeometry();
  const pos = new Float32Array(n * 3);
  const col = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) {
    // place on a wide flat-ish disc so they read as a sky.
    const r = 1.0 + Math.random() * 6.5;
    const a = Math.random() * Math.PI * 2;
    const y = (Math.random() - 0.4) * 4.0;
    pos[i*3+0] = Math.cos(a) * r;
    pos[i*3+1] = y;
    pos[i*3+2] = Math.sin(a) * r * 0.6;
    const tint = 0.7 + Math.random() * 0.3;
    col[i*3+0] = tint;
    col[i*3+1] = tint * (0.9 + Math.random() * 0.1);
    col[i*3+2] = 1.0;
  }
  geom.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geom.setAttribute('color', new THREE.BufferAttribute(col, 3));
  const mat = new THREE.PointsMaterial({
    size: 0.024,
    vertexColors: true,
    transparent: true,
    opacity: 0.95,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    sizeAttenuation: true,
  });
  return new THREE.Points(geom, mat);
}
