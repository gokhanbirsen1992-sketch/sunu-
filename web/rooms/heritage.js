import * as THREE from 'three';
import { Room } from '../lib/room.js';
import { makeSpriteTexture } from '../lib/env.js';

// Héritage — a cut-crystal decanter lit only by one candle.
export function createHeritage(canvas) {
  const room = new Room(canvas, {
    background: '#0c0703',
    envColors: { top: '#3a200e', bottom: '#06030a', horizon: '#1a0a05' },
    exposure: 1.0,
    fog: { color: '#0a0603', density: 0.18 },
  });
  room.cameraHome.set(-0.5, 1.05, 3.0);
  room.cameraLook.set(0.0, 0.9, 0.0);
  room.camera.position.copy(room.cameraHome);

  // Wooden table.
  const table = new THREE.Mesh(
    new THREE.BoxGeometry(3.0, 0.12, 1.6),
    new THREE.MeshPhysicalMaterial({
      color: '#3a1f10',
      roughness: 0.6,
      metalness: 0.1,
      clearcoat: 0.4,
      clearcoatRoughness: 0.5,
    }),
  );
  table.position.y = 0.0;
  table.receiveShadow = true;
  room.scene.add(table);

  // Decanter profile (lathe). Points go bottom -> top.
  const profile = [
    [0.00, 0.00],
    [0.42, 0.00],
    [0.45, 0.04],
    [0.46, 0.16],
    [0.44, 0.36],
    [0.38, 0.58],
    [0.30, 0.74],
    [0.18, 0.84],
    [0.13, 0.90],
    [0.12, 1.04],
    [0.16, 1.10],
    [0.14, 1.14],
    [0.00, 1.16],
  ].map(([x, y]) => new THREE.Vector2(x, y));

  const decGeom = new THREE.LatheGeometry(profile, 64);
  const crystal = new THREE.MeshPhysicalMaterial({
    color: '#f7eee0',
    metalness: 0.0,
    roughness: 0.04,
    transmission: 0.95,
    thickness: 0.6,
    ior: 1.55,
    attenuationColor: '#f0c98a',
    attenuationDistance: 0.9,
    clearcoat: 1.0,
    clearcoatRoughness: 0.04,
    envMapIntensity: 1.3,
  });
  const decanter = new THREE.Mesh(decGeom, crystal);
  decanter.position.y = 0.06;
  decanter.castShadow = true;
  room.scene.add(decanter);

  // Stopper.
  const stopper = new THREE.Mesh(
    new THREE.SphereGeometry(0.12, 32, 24),
    crystal,
  );
  stopper.position.y = 0.06 + 1.20;
  stopper.scale.y = 0.6;
  room.scene.add(stopper);

  // Liquid (amber).
  const liquid = new THREE.Mesh(
    new THREE.LatheGeometry(
      profile.filter(p => p.y <= 0.58).concat([new THREE.Vector2(0, 0.58)]),
      48,
    ),
    new THREE.MeshPhysicalMaterial({
      color: '#a45a1a',
      metalness: 0.0,
      roughness: 0.2,
      transmission: 0.6,
      thickness: 1.2,
      ior: 1.45,
      attenuationColor: '#8a4012',
      attenuationDistance: 0.5,
    }),
  );
  liquid.position.y = 0.06;
  room.scene.add(liquid);

  // Candle: brass holder + wax + flame sprite.
  const holder = new THREE.Mesh(
    new THREE.CylinderGeometry(0.10, 0.13, 0.04, 32),
    new THREE.MeshStandardMaterial({ color: '#8a6428', metalness: 1.0, roughness: 0.4 }),
  );
  holder.position.set(0.78, 0.08, 0.18);
  holder.castShadow = true;
  room.scene.add(holder);

  const wax = new THREE.Mesh(
    new THREE.CylinderGeometry(0.075, 0.075, 0.30, 24),
    new THREE.MeshStandardMaterial({ color: '#ecd8a8', roughness: 0.7 }),
  );
  wax.position.set(0.78, 0.25, 0.18);
  wax.castShadow = true;
  room.scene.add(wax);

  const wick = new THREE.Mesh(
    new THREE.CylinderGeometry(0.005, 0.005, 0.03, 6),
    new THREE.MeshStandardMaterial({ color: '#1a1106' }),
  );
  wick.position.set(0.78, 0.41, 0.18);
  room.scene.add(wick);

  const flameTex = makeSpriteTexture([
    [0.0,  'rgba(255,255,220,1)'],
    [0.15, 'rgba(255,200,120,0.9)'],
    [0.55, 'rgba(255,110,40,0.4)'],
    [1.0,  'rgba(40,0,0,0)'],
  ], 128);
  const flameMat = new THREE.SpriteMaterial({
    map: flameTex, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  });
  const flame = new THREE.Sprite(flameMat);
  flame.scale.set(0.18, 0.32, 1);
  flame.position.set(0.78, 0.48, 0.18);
  room.scene.add(flame);

  // The actual light from the candle.
  const candleLight = new THREE.PointLight('#ffb766', 4.5, 4.5, 1.8);
  candleLight.position.set(0.78, 0.50, 0.18);
  candleLight.castShadow = true;
  candleLight.shadow.mapSize.set(1024, 1024);
  candleLight.shadow.bias = -0.0006;
  room.scene.add(candleLight);

  // Soft ambient.
  room.scene.add(new THREE.AmbientLight('#1a0e05', 0.25));

  // A very faint cold rim so the silhouette reads against the dark.
  const rim = new THREE.PointLight('#3a4870', 0.3, 6, 1.5);
  rim.position.set(-1.6, 0.8, -0.8);
  room.scene.add(rim);

  room.update = (dt, t) => {
    // Candle flicker: combine three noises for organic motion.
    const f =
      Math.sin(t * 11.0) * 0.30 +
      Math.sin(t *  4.3 + 1.2) * 0.40 +
      Math.sin(t * 27.0 + 0.5) * 0.10;
    candleLight.intensity = 4.0 + f * 1.2;
    flame.scale.set(0.18 + f * 0.02, 0.32 + Math.abs(f) * 0.06, 1);
    flame.position.x = 0.78 + Math.sin(t * 6) * 0.004;
    decanter.rotation.y = Math.sin(t * 0.15) * 0.05;
    liquid.rotation.y = decanter.rotation.y;
    stopper.rotation.y = decanter.rotation.y;
  };

  return room;
}
