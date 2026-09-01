import React, { useEffect, useRef } from "react";
import * as THREE from "three";
import { useHermesState } from "../../state/useHermesState";

export const IntelligenceRings: React.FC = () => {
  const mountRef = useRef<HTMLDivElement>(null);
  const overview = useHermesState((s) => s.overview);

  useEffect(() => {
    if (!mountRef.current) return;

    const width = mountRef.current.clientWidth;
    const height = mountRef.current.clientHeight;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 0, 8);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    mountRef.current.appendChild(renderer.domElement);

    // 5 Concentric Rings
    const ringRadii = [1.2, 1.6, 2.0, 2.4, 2.8];
    const ringColors = [0x00ff88, 0x00f0ff, 0xffb800, 0x00bfff, 0x00f0ff];
    const rings: THREE.Mesh[] = [];

    ringRadii.forEach((radius, i) => {
      const geometry = new THREE.RingGeometry(radius, radius + 0.035, 64);
      const material = new THREE.MeshBasicMaterial({
        color: ringColors[i],
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.85,
      });
      const ring = new THREE.Mesh(geometry, material);
      scene.add(ring);
      rings.push(ring);
    });

    // Central 3D Hermes Emblem (Octahedron Prism)
    const emblemGeo = new THREE.OctahedronGeometry(0.5, 0);
    const emblemMat = new THREE.MeshStandardMaterial({
      color: 0xffb800,
      metalness: 0.9,
      roughness: 0.1,
      wireframe: true,
    });
    const emblem = new THREE.Mesh(emblemGeo, emblemMat);
    scene.add(emblem);

    const light = new THREE.PointLight(0x00f0ff, 2, 50);
    light.position.set(0, 0, 5);
    scene.add(light);

    let animId: number;
    const animate = () => {
      animId = requestAnimationFrame(animate);

      // Rotate rings at alternating harmonic frequencies
      rings.forEach((r, idx) => {
        r.rotation.z += 0.003 * (idx % 2 === 0 ? 1 : -1);
      });

      // Rotate central Hermes emblem
      emblem.rotation.x += 0.01;
      emblem.rotation.y += 0.015;

      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      if (!mountRef.current) return;
      const w = mountRef.current.clientWidth;
      const h = mountRef.current.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      cancelAnimationFrame(animId);
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  return (
    <div className="relative w-full h-[450px] flex items-center justify-center hermes-glass-card overflow-hidden">
      <div ref={mountRef} className="absolute inset-0 z-0" />
      
      {/* Telemetry Ring Status Overlay */}
      <div className="absolute bottom-4 left-6 right-6 z-10 flex justify-between text-xs text-slate-300">
        <div className="flex items-center space-x-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#00FF88] animate-pulse" />
          <span>Sourcing Stability: {overview?.intelligence_rings.ring_1_stability.value || "0.98"}</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#00F0FF]" />
          <span>Volatility Drift: {overview?.intelligence_rings.ring_2_volatility.value || "0.04"}</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#FFB800]" />
          <span>Lifecycle State: {overview?.intelligence_rings.ring_3_lifecycle.value || "ACTIVE"}</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#00BFFF]" />
          <span>Network Exposure: {overview?.intelligence_rings.ring_4_network.value || "4 Nodes"}</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#00FF88]" />
          <span>Economic Value: {overview?.intelligence_rings.ring_5_economic.value || "$12,450"}</span>
        </div>
      </div>
    </div>
  );
};
