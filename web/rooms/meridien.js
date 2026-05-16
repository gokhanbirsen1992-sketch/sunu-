import * as THREE from 'three';
import { Room } from '../lib/room.js';

// Méridien — a pocket watch suspended in a brass light.
export function createMeridien(canvas) {
  const room = new Room(canvas, {
    background: '#0e0a05',
    envColors: { top: '#a3793a', bottom: '#1a0e05', horizon: '#5d3c1a' },
    exposure: 1.0,
    fog: { color: '#0c0805', density: 0.10 },
  });
  room.cameraHome.set(-0.3, 1.1, 3.2);
  room.cameraLook.set(0.0, 1.0, 0.0);
  room.camera.position.copy(room.cameraHome);

  // Wall panel.
  const wall = new THREE.Mesh(
    new THREE.PlaneGeometry(14, 8),
    new THREE.MeshStandardMaterial({ color: '#16100a', roughness: 1.0 }),
  );
  wall.position.set(0, 2.5, -1.6);
  wall.receiveShadow = true;
  room.scene.add(wall);

  const goldMat = new THREE.MeshPhysicalMaterial({
    color: '#d8b257',
    metalness: 1.0,
    roughness: 0.22,
    clearcoat: 0.6,
    clearcoatRoughness: 0.18,
  });
  const goldMatDeep = new THREE.MeshStandardMaterial({
    color: '#8a6a2c', metalness: 1.0, roughness: 0.4,
  });

  // The watch — a small group hung from a chain.
  const watch = new THREE.Group();
  watch.position.set(0, 1.05, 0);
  room.scene.add(watch);

  // Case (cylinder).
  const caseMesh = new THREE.Mesh(
    new THREE.CylinderGeometry(0.42, 0.42, 0.10, 64),
    goldMat,
  );
  caseMesh.rotation.x = Math.PI / 2;
  caseMesh.castShadow = true;
  watch.add(caseMesh);

  // Bezel (torus on the front face).
  const bezel = new THREE.Mesh(
    new THREE.TorusGeometry(0.40, 0.022, 16, 96),
    goldMatDeep,
  );
  bezel.position.z = 0.055;
  watch.add(bezel);

  // Dial (off-white face).
  const dial = new THREE.Mesh(
    new THREE.CircleGeometry(0.38, 64),
    new THREE.MeshPhysicalMaterial({
      color: '#f1e6cf',
      roughness: 0.4,
      metalness: 0.0,
      clearcoat: 0.6,
      clearcoatRoughness: 0.25,
    }),
  );
  dial.position.z = 0.0555;
  watch.add(dial);

  // Hour indices.
  const idxMat = new THREE.MeshStandardMaterial({ color: '#2a1d10', roughness: 0.5 });
  for (let i = 0; i < 12; i++) {
    const big = i % 3 === 0;
    const idx = new THREE.Mesh(
      new THREE.BoxGeometry(big ? 0.018 : 0.010, big ? 0.05 : 0.028, 0.004),
      idxMat,
    );
    const a = (i / 12) * Math.PI * 2 - Math.PI / 2;
    idx.position.set(Math.cos(a) * 0.32, Math.sin(a) * 0.32, 0.058);
    idx.rotation.z = a + Math.PI / 2;
    watch.add(idx);
  }

  // Center cap + hands. Time held at "a quarter past five".
  const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.01, 16), goldMat);
  cap.rotation.x = Math.PI / 2; cap.position.z = 0.062; watch.add(cap);

  const handMat = new THREE.MeshStandardMaterial({ color: '#1a120a', roughness: 0.3, metalness: 0.5 });
  const hour = makeHand(0.16, 0.014, handMat);
  const minute = makeHand(0.24, 0.010, handMat);
  // 5:15  -> hour at ~157.5°, minute at 90° from 12. We rotate around Z (face is on Z).
  hour.rotation.z   = -((5 + 15/60) / 12) * Math.PI * 2;
  minute.rotation.z = -(15 / 60) * Math.PI * 2;
  hour.position.z = 0.061;
  minute.position.z = 0.062;
  watch.add(hour, minute);

  // Sub-second hand for life.
  const second = makeHand(0.27, 0.004, new THREE.MeshStandardMaterial({ color: '#8a3b2a' }));
  second.position.z = 0.0625;
  watch.add(second);

  // Chain — short fob of small torus links hanging up.
  const chain = new THREE.Group();
  const linkMat = goldMat;
  const linkCount = 10;
  for (let i = 0; i < linkCount; i++) {
    const link = new THREE.Mesh(
      new THREE.TorusGeometry(0.025, 0.008, 8, 16),
      linkMat,
    );
    link.position.y = 0.45 + i * 0.045;
    link.rotation.y = i % 2 ? 0 : Math.PI / 2;
    chain.add(link);
  }
  // Crown ring on top of the case.
  const bow = new THREE.Mesh(new THREE.TorusGeometry(0.04, 0.012, 8, 24), goldMatDeep);
  bow.position.y = 0.44;
  bow.rotation.x = Math.PI / 2;
  chain.add(bow);

  watch.add(chain);

  // Spotlight from above, warm.
  room.scene.add(new THREE.AmbientLight('#1d130a', 0.55));

  const lamp = new THREE.SpotLight('#ffcb7a', 18, 6, Math.PI / 8, 0.55, 1.3);
  lamp.position.set(0.2, 3.0, 0.8);
  lamp.target.position.set(0, 1.05, 0);
  lamp.castShadow = true;
  lamp.shadow.mapSize.set(1024, 1024);
  lamp.shadow.bias = -0.0006;
  room.scene.add(lamp, lamp.target);

  const fill = new THREE.PointLight('#5a2e16', 0.6, 4, 2);
  fill.position.set(-1.2, 1.0, 1.0);
  room.scene.add(fill);

  // Soft sway of the watch on its chain.
  room.update = (dt, t) => {
    watch.rotation.z = Math.sin(t * 0.7) * 0.05;
    watch.position.x = Math.sin(t * 0.7) * 0.04;
    second.rotation.z -= dt * (Math.PI * 2) / 60; // tick continuously
    // Lamp gently shifts like a chandelier swing.
    lamp.position.x = 0.2 + Math.sin(t * 0.3) * 0.15;
  };

  return room;
}

function makeHand(length, width, material) {
  const g = new THREE.Shape();
  g.moveTo(-width, -0.01);
  g.lineTo( width, -0.01);
  g.lineTo( width * 0.6, length);
  g.lineTo(-width * 0.6, length);
  g.closePath();
  const geom = new THREE.ExtrudeGeometry(g, { depth: 0.005, bevelEnabled: false });
  return new THREE.Mesh(geom, material);
}
