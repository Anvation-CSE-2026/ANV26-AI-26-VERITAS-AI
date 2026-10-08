import React, { useEffect, useRef } from 'react'

export default function LandingHeroCanvas({ scrollProgress = 0 }) {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

    let animationFrameId
    let width = (canvas.width = window.innerWidth)
    let height = (canvas.height = window.innerHeight)

    const handleResize = () => {
      if (!canvas) return
      width = canvas.width = window.innerWidth
      height = canvas.height = window.innerHeight
      initParticles()
    }
    window.addEventListener('resize', handleResize)

    // Node Types
    const types = [
      { name: 'clause', color: '#3B82F6', radius: 4 }, // Corporate blue
      { name: 'policy', color: '#5EEAD4', radius: 4.5 }, // Intelligence teal
      { name: 'risk', color: '#F97316', radius: 4 }, // Orange/Risk
      { name: 'evidence', color: '#34D399', radius: 3.5 }, // Emerald/Verified
      { name: 'obligation', color: '#A78BFA', radius: 3.5 }, // Lavender
    ]

    const PARTICLE_COUNT = Math.min(Math.floor((width * height) / 14000), 75)
    let particles = []

    function initParticles() {
      particles = []
      const cols = 8
      const rows = Math.ceil(PARTICLE_COUNT / cols)

      for (let i = 0; i < PARTICLE_COUNT; i++) {
        const type = types[i % types.length]
        // Free organic position
        const freeX = Math.random() * width
        const freeY = Math.random() * height
        // Structured grid position (for scroll transition)
        const col = i % cols
        const row = Math.floor(i / cols)
        const structuredX = (width * 0.15) + (col / (cols - 1)) * (width * 0.7)
        const structuredY = (height * 0.2) + (row / (rows - 1)) * (height * 0.6)

        particles.push({
          freeX,
          freeY,
          structuredX,
          structuredY,
          x: freeX,
          y: freeY,
          vx: (Math.random() - 0.5) * 0.6,
          vy: (Math.random() - 0.5) * 0.6,
          type,
          phase: Math.random() * Math.PI * 2,
        })
      }
    }

    initParticles()

    let mouseX = -1000
    let mouseY = -1000
    const handleMouseMove = (e) => {
      mouseX = e.clientX
      mouseY = e.clientY
    }
    window.addEventListener('mousemove', handleMouseMove)

    let currentProgress = scrollProgress

    const render = () => {
      // Smooth interpolation of scroll progress
      currentProgress += (scrollProgress - currentProgress) * 0.08

      ctx.clearRect(0, 0, width, height)

      // Background subtle gradient glow
      const radial = ctx.createRadialGradient(
        width * 0.5,
        height * 0.4,
        50,
        width * 0.5,
        height * 0.4,
        width * 0.7
      )
      radial.addColorStop(0, 'rgba(15, 23, 42, 0.4)')
      radial.addColorStop(1, 'rgba(11, 20, 38, 0)')
      ctx.fillStyle = radial
      ctx.fillRect(0, 0, width, height)

      // Calculate structure weight: 0 at top, ramps to 1 as user scrolls
      const structWeight = Math.min(Math.max((currentProgress - 0.15) / 0.5, 0), 1)

      // Update particle positions
      particles.forEach((p) => {
        if (!prefersReducedMotion) {
          p.freeX += p.vx
          p.freeY += p.vy

          if (p.freeX < 0 || p.freeX > width) p.vx *= -1
          if (p.freeY < 0 || p.freeY > height) p.vy *= -1
          p.phase += 0.02
        }

        // Interpolate between free floating and structured matrix
        const targetX = p.freeX * (1 - structWeight) + p.structuredX * structWeight
        const targetY = p.freeY * (1 - structWeight) + p.structuredY * structWeight

        p.x += (targetX - p.x) * 0.1
        p.y += (targetY - p.y) * 0.1

        // Mouse interaction
        const dx = mouseX - p.x
        const dy = mouseY - p.y
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist < 120 && !prefersReducedMotion) {
          p.x -= (dx / dist) * (120 - dist) * 0.04
          p.y -= (dy / dist) * (120 - dist) * 0.04
        }
      })

      // Draw connections
      const maxDist = structWeight > 0.5 ? 160 : 130
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const p1 = particles[i]
          const p2 = particles[j]
          const dx = p1.x - p2.x
          const dy = p1.y - p2.y
          const dist = Math.sqrt(dx * dx + dy * dy)

          if (dist < maxDist) {
            const alpha = (1 - dist / maxDist) * (0.15 + structWeight * 0.25)
            ctx.beginPath()
            ctx.strokeStyle = p1.type.color
            ctx.globalAlpha = alpha
            ctx.lineWidth = structWeight > 0.5 ? 1.2 : 0.8
            ctx.moveTo(p1.x, p1.y)
            ctx.lineTo(p2.x, p2.y)
            ctx.stroke()
          }
        }
      }

      // Draw nodes
      particles.forEach((p) => {
        const pulse = prefersReducedMotion ? 1 : 1 + Math.sin(p.phase) * 0.2
        const r = p.type.radius * pulse

        // Glow ring
        ctx.beginPath()
        ctx.arc(p.x, p.y, r * 2.2, 0, Math.PI * 2)
        ctx.fillStyle = p.type.color
        ctx.globalAlpha = 0.18
        ctx.fill()

        // Inner solid node
        ctx.beginPath()
        ctx.arc(p.x, p.y, r, 0, Math.PI * 2)
        ctx.fillStyle = p.type.color
        ctx.globalAlpha = 0.95
        ctx.fill()

        // Tiny center spark
        ctx.beginPath()
        ctx.arc(p.x, p.y, r * 0.4, 0, Math.PI * 2)
        ctx.fillStyle = '#FFFFFF'
        ctx.globalAlpha = 0.9
        ctx.fill()
      })

      ctx.globalAlpha = 1.0

      if (!prefersReducedMotion) {
        animationFrameId = requestAnimationFrame(render)
      }
    }

    render()

    return () => {
      window.removeEventListener('resize', handleResize)
      window.removeEventListener('mousemove', handleMouseMove)
      if (animationFrameId) cancelAnimationFrame(animationFrameId)
    }
  }, [scrollProgress])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      aria-hidden="true"
    />
  )
}

