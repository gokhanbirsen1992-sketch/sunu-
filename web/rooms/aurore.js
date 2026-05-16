import * as THREE from 'three';
import { Room } from '../lib/room.js';

// L'Aurore — a rose-gold solitaire under a slow, warm dawn.
export function createAurore(canvas) {
  const room = new Room(canvas, {
    background: '#1b1410',
    envColors: { top: '#f1c089', bottom: '#1a0e0a', horizon: '#d77a4a' },
    exposure: 1.05,
  });
  room.camera.fov = 30;
  room.camera.updateProjectionMatrix();
  room.cameraHome.set(0.0, 1.05, 3.5);
  room.cameraLook.set(0.0, 0.95, 0.0);
  room.camera.position.copy(room.cameraHome);

  // Velvet pedestal.
  const pedestal = new THREE.Mesh(
    new THREE.CylinderGeometry(1.2, 1.4, 0.18, 64),
    new THREE.MeshStandardMaterial({ color: '#2a1612', roughness: 0.95, metalness: 0.0 }),
  );
  pedestal.position.y = 0.09;
  pedestal.receiveShadow = true;
  room.scene.add(pedestal);

  // Soft cushion (squashed sphere).
  const cushion = new THREE.Mesh(
    new THREE.SphereGeometry(0.55, 48, 32),
    new THREE.MeshStandardMaterial({ color: '#3a1d18', roughness: 0.85 }),
  );
  cushion.scale.set(1.0, 0.35, 1.0);
  cushion.position.y = 0.22;
  cushion.receiveShadow = true;
  room.scene.add(cushion);

  // The ring band — rose gold.
  const band = new THREE.Mesh(
    new THREE.TorusGeometry(0.28, 0.045, 32, 96),
    new THREE.MeshPhysicalMaterial({
      color: '#e6a479',
      metalness: 1.0,
      roughness: 0.18,
      clearcoat: 0.7,
      clearcoatRoughness: 0.15,
    }),
  );
  band.rotation.x = Math.PI / 2;
  band.position.y = 0.48;
  band.castShadow = true;
  room.scene.add(band);

  // Four prongs.
  const prongMat = new THREE.MeshStandardMaterial({ color: '#e6a479', metalness: 1, roughness: 0.2 });
  const prongs = new THREE.Group();
  for (let i = 0; i < 4; i++) {
    const p = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.018, 0.18, 8), prongMat);
    const a = (i / 4) * Math.PI * 2 + Math.PI / 4;
    p.position.set(Math.cos(a) * 0.085, 0.62, Math.sin(a) * 0.085);
    prongs.add(p);
  }
  room.scene.add(prongs);

  // The stone — icosahedron with physical glass for fake brilliance.
  const stone = new THREE.Mesh(
    new THREE.IcosahedronGeometry(0.13, 0),
    new THREE.MeshPhysicalMaterial({
      color: '#ffffff',
      metalness: 0.0,
      roughness: 0.02,
      transmission: 1.0,
      thickness: 0.4,
      ior: 2.4,
      attenuationColor: '#ffe9d2',
      attenuationDistance: 0.6,
      clearcoat: 1.0,
      clearcoatRoughness: 0.0,
      envMapIntensity: 1.6,
    }),
  );
  stone.position.set(0, 0.69, 0);
  stone.castShadow = true;
  room.scene.add(stone);

  // Backdrop: tall warm panel + floor blend.
  const backdrop = new THREE.Mesh(
    new THREE.PlaneGeometry(20, 12),
    new THREE.MeshStandardMaterial({ color: '#1a0c08', roughness: 1, metalness: 0 }),
  );
  backdrop.position.set(0, 4, -3.2);
  room.scene.add(backdrop);

  // Lights — single window, warm.
  room.scene.add(new THREE.AmbientLight('#3a1f15', 0.45));

  const sun = new THREE.DirectionalLight('#ffb56a', 4.5);
  sun.position.set(-2.5, 2.4, 2.0);
  sun.castShadow = true;
  sun.shadow.mapSize.set(1024, 1024);
  sun.shadow.camera.near = 0.5;
  sun.shadow.camera.far = 8;
  sun.shadow.camera.left = -2; sun.shadow.camera.right = 2;
  sun.shadow.camera.top = 2; sun.shadow.camera.bottom = -2;
  sun.shadow.bias = -0.0008;
  room.scene.add(sun);

  const fill = new THREE.PointLight('#7a3f2a', 0.9, 6, 1.6);
  fill.position.set(1.6, 1.4, 1.2);
  room.scene.add(fill);

  const rim = new THREE.PointLight('#ffd1a0', 1.0, 5, 2.0);
  rim.position.set(0.0, 1.6, -1.0);
  room.scene.add(rim);

  // Slow rotation of the ring assembly.
  const assembly = new THREE.Group();
  assembly.add(band, prongs, stone);
  room.scene.add(assembly);

  room.update = (dt, t) => {
    assembly.rotation.y = t * 0.18;
    // breathe the sun a touch.
    sun.intensity = 4.2 + Math.sin(t * 0.4) * 0.4;
  };

  return room;
}
