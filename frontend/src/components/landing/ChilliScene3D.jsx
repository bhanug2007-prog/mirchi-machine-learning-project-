import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";

/**
 * Creates an organic Indian red chilli geometry (Guntur / Teja variety)
 * using lofted curved cross-sections with natural tapering, subtle ridges,
 * and realistic sickle-curve spine.
 */
function createChilliGeometry({
  length = 6.0,
  maxRadius = 0.68,
  curveStrength = 1.0,
  ribs = 4,
}) {
  const slices = 64;
  const radialSegments = 32;

  // Build curved spine points (natural organic sickle curve)
  const spinePoints = [
    new THREE.Vector3(0.35 * curveStrength, -length * 0.48, 0.15 * curveStrength), // tip
    new THREE.Vector3(0.18 * curveStrength, -length * 0.32, 0.08 * curveStrength),
    new THREE.Vector3(-0.08 * curveStrength, -length * 0.1, -0.04 * curveStrength),
    new THREE.Vector3(-0.18 * curveStrength, length * 0.15, -0.02 * curveStrength),
    new THREE.Vector3(-0.06 * curveStrength, length * 0.35, 0.02 * curveStrength),
    new THREE.Vector3(0.0, length * 0.48, 0.0), // calyx base (shoulder)
  ];

  const spine = new THREE.CatmullRomCurve3(spinePoints);
  const frenetFrames = spine.computeFrenetFrames(slices, false);

  const vertices = [];
  const normals = [];
  const uvs = [];
  const indices = [];

  for (let i = 0; i <= slices; i++) {
    const t = i / slices; // 0 = tip, 1 = calyx
    const pt = spine.getPointAt(t);
    const normal = frenetFrames.normals[i];
    const binormal = frenetFrames.binormals[i];

    // Radius profile: sharp tip -> gradual swelling -> broad shoulder -> slight neck tuck
    let rProfile = 0;
    if (t < 0.06) {
      rProfile = (t / 0.06) * 0.18; // sharp tapered tip
    } else if (t < 0.65) {
      // Swelling body
      const factor = (t - 0.06) / 0.59;
      rProfile = 0.18 + Math.sin(factor * Math.PI * 0.5) * (maxRadius - 0.18);
    } else if (t < 0.9) {
      // Broad shoulders
      rProfile = maxRadius;
    } else {
      // Slight tuck into calyx
      const factor = (t - 0.9) / 0.1;
      rProfile = maxRadius - factor * 0.12;
    }

    for (let j = 0; j <= radialSegments; j++) {
      const theta = (j / radialSegments) * Math.PI * 2;

      // Add organic longitudinal fluting / lobes (natural chilli skin folds)
      const flute = 1.0 + 0.065 * Math.cos(ribs * theta) + 0.03 * Math.sin(2 * theta + t * 3.0);
      const r = rProfile * flute;

      const cosTheta = Math.cos(theta);
      const sinTheta = Math.sin(theta);

      // Radial vector in Frenet plane
      const vx = normal.x * cosTheta + binormal.x * sinTheta;
      const vy = normal.y * cosTheta + binormal.y * sinTheta;
      const vz = normal.z * cosTheta + binormal.z * sinTheta;

      vertices.push(pt.x + vx * r, pt.y + vy * r, pt.z + vz * r);

      // Normal
      const normLen = Math.hypot(vx, vy, vz) || 1;
      normals.push(vx / normLen, vy / normLen, vz / normLen);

      uvs.push(j / radialSegments, t);
    }
  }

  // Generate triangle faces
  for (let i = 0; i < slices; i++) {
    for (let j = 0; j < radialSegments; j++) {
      const a = i * (radialSegments + 1) + j;
      const b = (i + 1) * (radialSegments + 1) + j;
      const c = (i + 1) * (radialSegments + 1) + (j + 1);
      const d = i * (radialSegments + 1) + (j + 1);

      indices.push(a, b, d);
      indices.push(b, c, d);
    }
  }

  const geom = new THREE.BufferGeometry();
  geom.setIndex(indices);
  geom.setAttribute("position", new THREE.Float32BufferAttribute(vertices, 3));
  geom.setAttribute("normal", new THREE.Float32BufferAttribute(normals, 3));
  geom.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
  geom.computeVertexNormals();

  return geom;
}

/**
 * Creates green calyx and curved stem (pedicel)
 */
function createCalyxAndStemGroup({ length = 6.0, stemLength = 1.6, curveStrength = 1.0 }) {
  const group = new THREE.Group();

  // 1. Calyx Cap (Cap at top of chilli shoulder)
  const calyxGeom = new THREE.CylinderGeometry(0.55, 0.62, 0.35, 16, 2, true);
  const calyxMat = new THREE.MeshStandardMaterial({
    color: 0x2e5c26,
    roughness: 0.62,
    metalness: 0.08,
  });
  const calyxMesh = new THREE.Mesh(calyxGeom, calyxMat);
  calyxMesh.position.set(0, length * 0.48, 0);
  group.add(calyxMesh);

  // 2. Star Sepals (5 organic leaf teeth clinging to shoulder)
  const sepalsCount = 5;
  for (let s = 0; s < sepalsCount; s++) {
    const angle = (s / sepalsCount) * Math.PI * 2;
    const sepalGeom = new THREE.ConeGeometry(0.16, 0.45, 4);
    sepalGeom.rotateX(Math.PI); // point downwards
    const sepalMesh = new THREE.Mesh(sepalGeom, calyxMat);

    const radius = 0.52;
    sepalMesh.position.set(
      Math.cos(angle) * radius,
      length * 0.48 - 0.15,
      Math.sin(angle) * radius
    );
    sepalMesh.rotation.z = Math.cos(angle) * 0.4;
    sepalMesh.rotation.x = -Math.sin(angle) * 0.4;
    group.add(sepalMesh);
  }

  // 3. Curved Pedicel (Stem)
  const stemPoints = [
    new THREE.Vector3(0, length * 0.49, 0),
    new THREE.Vector3(0.08 * curveStrength, length * 0.49 + stemLength * 0.35, 0.04),
    new THREE.Vector3(0.24 * curveStrength, length * 0.49 + stemLength * 0.72, 0.12),
    new THREE.Vector3(0.42 * curveStrength, length * 0.49 + stemLength, 0.22),
  ];
  const stemCurve = new THREE.CatmullRomCurve3(stemPoints);
  const stemGeom = new THREE.TubeGeometry(stemCurve, 20, 0.09, 8, false);
  const stemMat = new THREE.MeshStandardMaterial({
    color: 0x3d7030,
    roughness: 0.75,
    metalness: 0.05,
  });
  const stemMesh = new THREE.Mesh(stemGeom, stemMat);
  group.add(stemMesh);

  return group;
}

/**
 * Assembles a complete realistic chilli object
 */
function buildChilli({
  chilliColor = 0xc9182b,
  length = 5.6,
  maxRadius = 0.65,
  curveStrength = 1.0,
  scale = 1.0,
}) {
  const container = new THREE.Group();

  // Main chilli flesh material
  const bodyMat = new THREE.MeshPhysicalMaterial({
    color: new THREE.Color(chilliColor),
    emissive: new THREE.Color(0x2b0407),
    roughness: 0.28,
    metalness: 0.04,
    clearcoat: 0.85,
    clearcoatRoughness: 0.2,
    sheen: 0.65,
    sheenColor: new THREE.Color(0xff4d5a),
    sheenRoughness: 0.3,
    reflectivity: 0.6,
  });

  const bodyGeom = createChilliGeometry({ length, maxRadius, curveStrength });
  const bodyMesh = new THREE.Mesh(bodyGeom, bodyMat);
  bodyMesh.castShadow = true;
  bodyMesh.receiveShadow = true;
  container.add(bodyMesh);

  // Calyx & Stem
  const calyx = createCalyxAndStemGroup({ length, stemLength: 1.5, curveStrength });
  container.add(calyx);

  container.scale.set(scale, scale, scale);
  return container;
}

export default function ChilliScene3D({ onExploreClick }) {
  const mountRef = useRef(null);
  const [isWebGLSupported, setIsWebGLSupported] = useState(true);
  const [isInteracting, setIsInteracting] = useState(false);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    // Check WebGL availability
    try {
      const testCanvas = document.createElement("canvas");
      const gl = testCanvas.getContext("webgl") || testCanvas.getContext("experimental-webgl");
      if (!gl) {
        setIsWebGLSupported(false);
        return;
      }
    } catch (e) {
      setIsWebGLSupported(false);
      return;
    }

    const width = container.clientWidth || 600;
    const height = container.clientHeight || 550;

    // Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100);
    camera.position.set(0, 0, 11.5);

    const renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
      powerPreference: "high-performance",
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;
    container.appendChild(renderer.domElement);

    // Master Group for mouse parallax & rotation
    const masterGroup = new THREE.Group();
    scene.add(masterGroup);

    // ─── 1. HERO MAIN CHILLI ───
    const heroChilli = buildChilli({
      chilliColor: 0xd90429,
      length: 6.2,
      maxRadius: 0.72,
      curveStrength: 1.1,
      scale: 1.05,
    });
    heroChilli.position.set(0.1, -0.1, 0.4);
    heroChilli.rotation.set(-0.25, 0.4, -0.32);
    masterGroup.add(heroChilli);

    // ─── 2. SECONDARY MIDGROUND CHILLI ───
    const secondaryChilli = buildChilli({
      chilliColor: 0xbd1026,
      length: 5.2,
      maxRadius: 0.58,
      curveStrength: 0.9,
      scale: 0.72,
    });
    secondaryChilli.position.set(-2.6, 1.4, -1.8);
    secondaryChilli.rotation.set(0.35, -0.6, 0.65);
    masterGroup.add(secondaryChilli);

    // ─── 3. TERTIARY ACCENT CHILLI (Depth element) ───
    const accentChilli = buildChilli({
      chilliColor: 0x9b0e1e,
      length: 4.8,
      maxRadius: 0.52,
      curveStrength: 1.25,
      scale: 0.58,
    });
    accentChilli.position.set(2.4, -1.8, -2.4);
    accentChilli.rotation.set(0.65, 0.8, -0.75);
    masterGroup.add(accentChilli);

    // ─── 4. AMBIENT SPICE PARTICLES & GOLDEN MOTES ───
    const particleCount = 70;
    const particleGeom = new THREE.BufferGeometry();
    const particlePositions = new Float32Array(particleCount * 3);
    const particleVelocities = [];

    for (let p = 0; p < particleCount; p++) {
      particlePositions[p * 3] = (Math.random() - 0.5) * 12;
      particlePositions[p * 3 + 1] = (Math.random() - 0.5) * 10;
      particlePositions[p * 3 + 2] = (Math.random() - 0.5) * 8;

      particleVelocities.push({
        y: 0.003 + Math.random() * 0.006,
        x: (Math.random() - 0.5) * 0.003,
        rot: Math.random() * 0.02,
      });
    }

    particleGeom.setAttribute("position", new THREE.BufferAttribute(particlePositions, 3));
    const particleMat = new THREE.PointsMaterial({
      color: 0xffa040,
      size: 0.08,
      transparent: true,
      opacity: 0.75,
      blending: THREE.AdditiveBlending,
    });
    const particleSystem = new THREE.Points(particleGeom, particleMat);
    scene.add(particleSystem);

    // ─── 5. LIGHTING ───
    // Key directional studio light (bright warm)
    const keyLight = new THREE.DirectionalLight(0xffffff, 2.8);
    keyLight.position.set(5, 7, 7);
    keyLight.castShadow = true;
    scene.add(keyLight);

    // Fill crimson rim light (gives rich red glow on shadow side)
    const fillLight = new THREE.DirectionalLight(0xff2b44, 2.2);
    fillLight.position.set(-6, -4, 4);
    scene.add(fillLight);

    // Agricultural cool emerald rim light from behind (luxury contrast on stems & edges)
    const rimLight = new THREE.DirectionalLight(0x34d399, 1.8);
    rimLight.position.set(0, 5, -6);
    scene.add(rimLight);

    // Soft ambient
    const ambientLight = new THREE.AmbientLight(0x1a1215, 1.4);
    scene.add(ambientLight);

    // Warm point light near hero chilli for specular glint
    const glintLight = new THREE.PointLight(0xffaa77, 1.5, 8);
    glintLight.position.set(1.5, 1.5, 3);
    scene.add(glintLight);

    // ─── MOUSE & INTERACTION HANDLING ───
    let mouseX = 0;
    let mouseY = 0;
    let targetRotX = 0;
    let targetRotY = 0;
    let isDragging = false;
    let prevMousePos = { x: 0, y: 0 };
    let dragVelocity = { x: 0, y: 0 };

    const handleMouseMove = (e) => {
      const rect = container.getBoundingClientRect();
      const nx = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const ny = -(((e.clientY - rect.top) / rect.height) * 2 - 1);
      mouseX = nx;
      mouseY = ny;

      if (isDragging) {
        const deltaX = e.clientX - prevMousePos.x;
        const deltaY = e.clientY - prevMousePos.y;
        dragVelocity.x = deltaX * 0.008;
        dragVelocity.y = deltaY * 0.008;
        heroChilli.rotation.y += dragVelocity.x;
        heroChilli.rotation.x += dragVelocity.y;
        prevMousePos = { x: e.clientX, y: e.clientY };
      }
    };

    const handleMouseDown = (e) => {
      isDragging = true;
      setIsInteracting(true);
      prevMousePos = { x: e.clientX, y: e.clientY };
    };

    const handleMouseUp = () => {
      isDragging = false;
      setIsInteracting(false);
    };

    const handleTouchMove = (e) => {
      if (e.touches.length > 0) {
        const touch = e.touches[0];
        const rect = container.getBoundingClientRect();
        mouseX = ((touch.clientX - rect.left) / rect.width) * 2 - 1;
        mouseY = -(((touch.clientY - rect.top) / rect.height) * 2 - 1);
      }
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    container.addEventListener("mousedown", handleMouseDown);
    container.addEventListener("touchmove", handleTouchMove, { passive: true });

    // Handle Resize
    const handleResize = () => {
      if (!container) return;
      const nw = container.clientWidth;
      const nh = container.clientHeight;
      camera.aspect = nw / nh;
      camera.updateProjectionMatrix();
      renderer.setSize(nw, nh);
    };
    window.addEventListener("resize", handleResize);

    // ─── ANIMATION LOOP ───
    let animationId;
    let clock = new THREE.Clock();

    const animate = () => {
      animationId = requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();

      // Gentle floating levitation
      const floatHero = Math.sin(elapsedTime * 1.3) * 0.16;
      heroChilli.position.y = -0.1 + floatHero;

      const floatSec = Math.sin(elapsedTime * 1.1 + 1.2) * 0.14;
      secondaryChilli.position.y = 1.4 + floatSec;

      const floatAcc = Math.cos(elapsedTime * 0.9 + 2.0) * 0.18;
      accentChilli.position.y = -1.8 + floatAcc;

      // Slow majestic continuous idle rotation (slows slightly if dragged)
      if (!isDragging) {
        heroChilli.rotation.y += 0.004;
        heroChilli.rotation.z += Math.sin(elapsedTime * 0.5) * 0.001;

        secondaryChilli.rotation.y -= 0.0035;
        secondaryChilli.rotation.x += Math.sin(elapsedTime * 0.6) * 0.0015;

        accentChilli.rotation.y += 0.003;
      }

      // Parallax mouse follow on master group (smooth damping)
      targetRotY = mouseX * 0.35;
      targetRotX = -mouseY * 0.25;
      masterGroup.rotation.y += (targetRotY - masterGroup.rotation.y) * 0.05;
      masterGroup.rotation.x += (targetRotX - masterGroup.rotation.x) * 0.05;

      // Animate floating particles
      const positions = particleSystem.geometry.attributes.position.array;
      for (let p = 0; p < particleCount; p++) {
        positions[p * 3 + 1] += particleVelocities[p].y;
        positions[p * 3] += particleVelocities[p].x;

        // Wrap around bounds
        if (positions[p * 3 + 1] > 5) positions[p * 3 + 1] = -5;
        if (positions[p * 3] > 6) positions[p * 3] = -6;
        if (positions[p * 3] < -6) positions[p * 3] = 6;
      }
      particleSystem.geometry.attributes.position.needsUpdate = true;
      particleSystem.rotation.y = elapsedTime * 0.02;

      renderer.render(scene, camera);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
      window.removeEventListener("resize", handleResize);
      container.removeEventListener("mousedown", handleMouseDown);
      container.removeEventListener("touchmove", handleTouchMove);
      if (renderer.domElement && container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  return (
    <div className="relative w-full h-[480px] sm:h-[550px] lg:h-[620px] flex items-center justify-center select-none">
      {/* Ambient background glow aura */}
      <div className="absolute inset-0 bg-gradient-radial from-[#E63946]/18 via-[#C81D25]/06 to-transparent blur-3xl pointer-events-none rounded-full transform scale-90" />
      <div className="absolute w-72 h-72 bg-[#10B981]/10 blur-3xl rounded-full top-1/4 -right-10 pointer-events-none" />

      {/* 3D Canvas Mount */}
      {isWebGLSupported ? (
        <div
          ref={mountRef}
          className={`w-full h-full cursor-grab active:cursor-grabbing transition-opacity duration-700 ${
            isInteracting ? "cursor-grabbing" : ""
          }`}
          title="Drag to interact and rotate chillies in 3D"
        />
      ) : (
        /* WebGL Fallback: Layered high-res realistic chilli visual */
        <div className="relative w-full h-full flex items-center justify-center p-6">
          <div className="relative w-[340px] sm:w-[420px] rounded-3xl overflow-hidden border border-white/10 shadow-2xl bg-gradient-to-b from-white/5 to-white/0 backdrop-blur-md p-4 group">
            <img
              src="/harvested_chillies.jpg"
              alt="Indian Red Chillies"
              className="w-full h-[360px] object-cover rounded-2xl group-hover:scale-105 transition-transform duration-700"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-[#0B0D0E] via-transparent to-transparent rounded-2xl" />
            <div className="absolute bottom-6 left-6 right-6 flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-wider text-[#FF4D5A] font-semibold">Guntur Teja S17</p>
                <p className="text-white text-base font-bold">Premium Quality Chilli</p>
              </div>
              <span className="px-3 py-1 text-xs rounded-full bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/30 font-medium">
                Live Yard
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Interactive 3D Badge Indicator */}
      <div className="absolute bottom-3 right-4 sm:right-8 flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#13161F]/80 border border-white/10 backdrop-blur-md shadow-lg pointer-events-none">
        <span className="w-2 h-2 rounded-full bg-[#E63946] animate-ping" />
        <span className="text-[11px] font-medium text-slate-300 tracking-wide uppercase">
          Real-time 3D • Drag to Rotate
        </span>
      </div>

      {/* Floating Quality Spec Tag */}
      <div className="absolute top-8 left-2 sm:left-6 px-4 py-2.5 rounded-2xl bg-[#0F121C]/85 border border-[#E63946]/25 backdrop-blur-md shadow-xl pointer-events-none animate-float hidden sm:flex items-center gap-3">
        <div className="w-8 h-8 rounded-xl bg-[#E63946]/15 flex items-center justify-center text-sm border border-[#E63946]/30">
          🌶️
        </div>
        <div>
          <p className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider">Variety Target</p>
          <p className="text-xs font-bold text-white">Guntur S17 & 334 Sannam</p>
        </div>
      </div>
    </div>
  );
}
