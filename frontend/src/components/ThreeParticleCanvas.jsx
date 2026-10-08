import React, { useEffect, useRef } from 'react'
import * as THREE from 'three'

export default function ThreeParticleCanvas({ scrollProgress = 0, mousePos = { x: 0, y: 0 } }) {
  const mountRef = useRef(null)
  const sceneRef = useRef(null)
  const rendererRef = useRef(null)
  const materialRef = useRef(null)
  const cameraRef = useRef(null)
  const reqIdRef = useRef(null)

  useEffect(() => {
    const container = mountRef.current
    if (!container) return

    const width = container.clientWidth || window.innerWidth
    const height = container.clientHeight || window.innerHeight

    // 1. Scene, Camera, Renderer
    const scene = new THREE.Scene()
    scene.fog = new THREE.FogExp2(0x080B0A, 0.04)
    sceneRef.current = scene

    const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 100)
    camera.position.set(0, 0, 9)
    cameraRef.current = camera

    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance',
    })
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.setSize(width, height)
    renderer.setClearColor(0x080B0A, 1.0)
    rendererRef.current = renderer
    container.appendChild(renderer.domElement)

    // 2. Generate 18,000 Particles Across 5 Deterministic Formations
    const PARTICLE_COUNT = 18000
    const geometry = new THREE.BufferGeometry()

    const pos0 = new Float32Array(PARTICLE_COUNT * 3) // Formation 1: Celestial Torus Ring
    const pos1 = new Float32Array(PARTICLE_COUNT * 3) // Formation 2: Helical Infinity Wave
    const pos2 = new Float32Array(PARTICLE_COUNT * 3) // Formation 3: Undulating Terrain
    const pos3 = new Float32Array(PARTICLE_COUNT * 3) // Formation 4: Tripartite Evidence Clusters
    const pos4 = new Float32Array(PARTICLE_COUNT * 3) // Formation 5: Accretion Disc Galaxy
    const randoms = new Float32Array(PARTICLE_COUNT * 3) // Per-particle phase & speed

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const i3 = i * 3
      const u = Math.random()
      const v = Math.random()
      const w = Math.random()

      // Random attributes
      randoms[i3] = Math.random()
      randoms[i3 + 1] = Math.random() * Math.PI * 2
      randoms[i3 + 2] = 0.5 + Math.random() * 1.5

      // FORMATION 1: Large Glowing Torus Vortex (Scene 1)
      const theta1 = u * Math.PI * 2
      const phi1 = v * Math.PI * 2
      const majorRadius = 3.6 + (w - 0.5) * 1.2
      const minorRadius = 0.8 + Math.random() * 0.9
      pos0[i3] = (majorRadius + minorRadius * Math.cos(phi1)) * Math.cos(theta1)
      pos0[i3 + 1] = (majorRadius + minorRadius * Math.cos(phi1)) * Math.sin(theta1) * 0.65
      pos0[i3 + 2] = minorRadius * Math.sin(phi1) * 2.2 + (Math.random() - 0.5) * 0.5

      // FORMATION 2: Helical Infinity Wave / Corkscrew Stream (Scene 2)
      const t2 = (u - 0.5) * 14.0
      const helixRadius = 1.6 + Math.sin(t2 * 1.5) * 0.8 + (v - 0.5) * 0.9
      const helixAngle = t2 * 2.2 + phi1
      pos1[i3] = t2 * 1.1 + Math.sin(t2 * 0.5) * 1.5
      pos1[i3 + 1] = helixRadius * Math.sin(helixAngle) + Math.cos(t2 * 1.2) * 0.8
      pos1[i3 + 2] = helixRadius * Math.cos(helixAngle) * 1.4

      // FORMATION 3: Vast Harmonic Undulating Terrain (Scene 3)
      const x3 = (u - 0.5) * 15.0
      const z3 = (v - 0.5) * 12.0
      const dist3 = Math.sqrt(x3 * x3 + z3 * z3)
      const y3 = Math.sin(x3 * 0.9 + z3 * 0.6) * 1.2 + Math.cos(dist3 * 1.2) * 0.6 + (w - 0.5) * 0.4
      pos2[i3] = x3
      pos2[i3 + 1] = y3 - 0.5
      pos2[i3 + 2] = z3 - 1.0

      // FORMATION 4: Tripartite Evidence Clusters with Linking Bridges (Scene 4)
      const clusterIdx = i % 3
      let cx = 0
      let cy = 0
      let cz = 0
      if (clusterIdx === 0) {
        cx = -3.8 // Contract Clause (left)
        cy = 0.2
      } else if (clusterIdx === 1) {
        cx = 0.0 // Company Policy (center)
        cy = -0.4
      } else {
        cx = 3.8 // Verified Finding (right)
        cy = 0.3
      }

      // 80% in orb clusters, 20% in connecting stream tendrils
      if (w < 0.8) {
        const rad = 1.3 * Math.cbrt(Math.random())
        const cPhi = Math.acos(2 * Math.random() - 1)
        const cTheta = Math.random() * Math.PI * 2
        pos3[i3] = cx + rad * Math.sin(cPhi) * Math.cos(cTheta)
        pos3[i3 + 1] = cy + rad * Math.sin(cPhi) * Math.sin(cTheta)
        pos3[i3 + 2] = cz + rad * Math.cos(cPhi)
      } else {
        // Connecting bridges between clusters
        const bridgeT = (Math.random() - 0.5) * 8.0
        pos3[i3] = bridgeT
        pos3[i3 + 1] = Math.sin(bridgeT * 1.2) * 0.4 + (Math.random() - 0.5) * 0.3
        pos3[i3 + 2] = (Math.random() - 0.5) * 0.6
      }

      // FORMATION 5: Planetary Accretion Disc Galaxy (Scene 5)
      const r5 = 1.2 + Math.pow(Math.random(), 0.6) * 5.0
      const theta5 = Math.random() * Math.PI * 2
      const spiralOffset = r5 * 1.8
      pos4[i3] = r5 * Math.cos(theta5 + spiralOffset)
      pos4[i3 + 1] = r5 * Math.sin(theta5 + spiralOffset) * 0.45 + (Math.random() - 0.5) * (0.2 + r5 * 0.08)
      pos4[i3 + 2] = (Math.random() - 0.5) * (0.4 + r5 * 0.15)
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(pos0, 3))
    geometry.setAttribute('aPos0', new THREE.BufferAttribute(pos0, 3))
    geometry.setAttribute('aPos1', new THREE.BufferAttribute(pos1, 3))
    geometry.setAttribute('aPos2', new THREE.BufferAttribute(pos2, 3))
    geometry.setAttribute('aPos3', new THREE.BufferAttribute(pos3, 3))
    geometry.setAttribute('aPos4', new THREE.BufferAttribute(pos4, 3))
    geometry.setAttribute('aRandom', new THREE.BufferAttribute(randoms, 3))

    // 3. Custom GLSL Shader Material with Morphing & Wave Flow
    const vertexShader = `
      uniform float uProgress;
      uniform float uTime;
      uniform float uPixelRatio;
      uniform vec2 uMouse;

      attribute vec3 aPos0;
      attribute vec3 aPos1;
      attribute vec3 aPos2;
      attribute vec3 aPos3;
      attribute vec3 aPos4;
      attribute vec3 aRandom;

      varying vec3 vColor;
      varying float vAlpha;

      void main() {
        // Piecewise smooth interpolation across 5 scenes: [0..1], [1..2], [2..3], [3..4]
        vec3 p0 = aPos0;
        vec3 p1 = aPos1;
        vec3 p2 = aPos2;
        vec3 p3 = aPos3;
        vec3 p4 = aPos4;

        vec3 blendedPos = p0;
        float p = clamp(uProgress, 0.0, 4.0);

        if (p < 1.0) {
          float t = smoothstep(0.0, 1.0, p);
          blendedPos = mix(p0, p1, t);
        } else if (p < 2.0) {
          float t = smoothstep(0.0, 1.0, p - 1.0);
          blendedPos = mix(p1, p2, t);
        } else if (p < 3.0) {
          float t = smoothstep(0.0, 1.0, p - 2.0);
          blendedPos = mix(p2, p3, t);
        } else {
          float t = smoothstep(0.0, 1.0, p - 3.0);
          blendedPos = mix(p3, p4, t);
        }

        // Harmonic continuous organic wave & breathing deformation
        float waveTime = uTime * 0.45 + aRandom.y;
        float waveAmp = 0.16 * aRandom.z;
        blendedPos.x += sin(waveTime + blendedPos.y * 1.2) * waveAmp;
        blendedPos.y += cos(waveTime * 1.1 + blendedPos.x * 1.0) * waveAmp;
        blendedPos.z += sin(waveTime * 0.8 + blendedPos.z * 1.4) * (waveAmp * 1.5);

        // Subtle interactive mouse influence
        blendedPos.x += uMouse.x * 0.35 * (1.0 - length(blendedPos.xy) * 0.08);
        blendedPos.y += uMouse.y * 0.35 * (1.0 - length(blendedPos.xy) * 0.08);

        vec4 mvPosition = modelViewMatrix * vec4(blendedPos, 1.0);
        gl_Position = projectionMatrix * mvPosition;

        // Size attenuation with perspective
        float pointBaseSize = 22.0 * uPixelRatio;
        gl_PointSize = (pointBaseSize / -mvPosition.z) * (0.7 + aRandom.x * 0.7);

        // Depth & Mint Color Palette (#C5F5D5 & #A8E6BF & #8A9B91)
        vec3 mintBright = vec3(0.772, 0.961, 0.835); // #C5F5D5
        vec3 mintAccent = vec3(0.659, 0.902, 0.749); // #A8E6BF
        vec3 mintDeep   = vec3(0.35, 0.46, 0.40);

        float depthFactor = smoothstep(14.0, 4.0, -mvPosition.z);
        vColor = mix(mintDeep, mix(mintAccent, mintBright, aRandom.x), depthFactor);
        vAlpha = (0.35 + depthFactor * 0.65) * (0.6 + sin(waveTime * 2.0) * 0.2);
      }
    `

    const fragmentShader = `
      varying vec3 vColor;
      varying float vAlpha;

      void main() {
        // Perfectly smooth circular glowing particle with gaussian falloff
        vec2 coord = gl_PointCoord - vec2(0.5);
        float dist = length(coord);
        if (dist > 0.5) discard;

        float intensity = smoothstep(0.5, 0.0, dist);
        intensity = pow(intensity, 1.4);

        gl_FragColor = vec4(vColor, vAlpha * intensity * 0.9);
      }
    `

    const material = new THREE.ShaderMaterial({
      vertexShader,
      fragmentShader,
      uniforms: {
        uProgress: { value: 0.0 },
        uTime: { value: 0.0 },
        uPixelRatio: { value: Math.min(window.devicePixelRatio, 2) },
        uMouse: { value: new THREE.Vector2(0, 0) },
      },
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    })
    materialRef.current = material

    const particleSystem = new THREE.Points(geometry, material)
    scene.add(particleSystem)

    // 4. Animation Render Loop
    let clock = new THREE.Clock()

    const animate = () => {
      const elapsedTime = clock.getElapsedTime()
      if (materialRef.current) {
        materialRef.current.uniforms.uTime.value = elapsedTime
      }

      // Gentle camera orbit / breath
      if (cameraRef.current) {
        cameraRef.current.position.x = Math.sin(elapsedTime * 0.12) * 0.35
        cameraRef.current.position.y = Math.cos(elapsedTime * 0.15) * 0.25
        cameraRef.current.lookAt(0, 0, 0)
      }

      renderer.render(scene, camera)
      reqIdRef.current = requestAnimationFrame(animate)
    }

    animate()

    // 5. Responsive Resize Handler
    const handleResize = () => {
      if (!container || !camera || !renderer) return
      const w = container.clientWidth || window.innerWidth
      const h = container.clientHeight || window.innerHeight
      camera.aspect = w / h
      camera.updateProjectionMatrix()
      renderer.setSize(w, h)
      if (materialRef.current) {
        materialRef.current.uniforms.uPixelRatio.value = Math.min(window.devicePixelRatio, 2)
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      if (reqIdRef.current) cancelAnimationFrame(reqIdRef.current)
      if (renderer.domElement && container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement)
      }
      geometry.dispose()
      material.dispose()
      renderer.dispose()
    }
  }, [])

  // Sync scrollProgress & mouse movement to shader uniforms
  useEffect(() => {
    if (materialRef.current) {
      // scrollProgress ranges 0.0 to 1.0; map to uProgress 0.0 to 4.0
      materialRef.current.uniforms.uProgress.value = scrollProgress * 4.0
      materialRef.current.uniforms.uMouse.value.set(mousePos.x, mousePos.y)
    }
  }, [scrollProgress, mousePos])

  return (
    <div
      ref={mountRef}
      className="fixed inset-0 w-full h-full pointer-events-none z-0 overflow-hidden"
      aria-hidden="true"
    />
  )
}

