import React, { useEffect, useRef, useState } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import ThreeParticleCanvas from './ThreeParticleCanvas'
import { useAuth } from '../context/useAuth'

gsap.registerPlugin(ScrollTrigger)

export default function LandingPage({ onLaunchWorkspace, onLoadDemo, onOpenPricing }) {
  const containerRef = useRef(null)
  const [scrollProgress, setScrollProgress] = useState(0)
  const [currentSceneIdx, setCurrentSceneIdx] = useState(0)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
  const { isAuthenticated, openAuthModal } = useAuth()

  // Track mouse for subtle interactive parallax
  useEffect(() => {
    const handleMouseMove = (e) => {
      const x = (e.clientX / window.innerWidth) * 2 - 1
      const y = -(e.clientY / window.innerHeight) * 2 + 1
      setMousePos({ x, y })
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  // GSAP ScrollTrigger Scrubbed Timeline
  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const trigger = ScrollTrigger.create({
      trigger: container,
      start: 'top top',
      end: 'bottom bottom',
      scrub: 0.6,
      onUpdate: (self) => {
        const prog = self.progress
        setScrollProgress(prog)
        const idx = Math.min(Math.floor(prog * 5), 4)
        setCurrentSceneIdx(idx)
      },
    })

    return () => {
      trigger.kill()
    }
  }, [])

  const scrollToScene = (index) => {
    const totalHeight = containerRef.current?.clientHeight || window.innerHeight * 5
    const targetY = (index / 4) * (totalHeight - window.innerHeight)
    window.scrollTo({ top: targetY, behavior: 'smooth' })
  }

  // Calculate opacity and translation for each of the 5 scenes based on scrollProgress
  const getSceneStyle = (index) => {
    const sceneCenter = index * 0.25
    const dist = Math.abs(scrollProgress - sceneCenter)
    const opacity = Math.max(0, 1 - dist * 5.2)
    const translateY = (scrollProgress - sceneCenter) * 120
    const isPointerEvents = opacity > 0.4 ? 'pointer-events-auto' : 'pointer-events-none'

    return {
      opacity,
      transform: `translateY(${translateY}px)`,
      transition: 'opacity 0.25s ease-out, transform 0.25s ease-out',
      pointerEvents: isPointerEvents ? 'auto' : 'none',
      visibility: opacity > 0.01 ? 'visible' : 'hidden',
    }
  }

  return (
    <div
      ref={containerRef}
      className="relative bg-[#080B0A] text-[#F2F5F0] selection:bg-[#C5F5D5] selection:text-[#080B0A]"
      style={{ height: '500vh' }}
    >
      {/* 3D WebGL Fluid Particle Experience */}
      <ThreeParticleCanvas scrollProgress={scrollProgress} mousePos={mousePos} />

      {/* Persistent Atmospheric HUD & Navigation */}
      <div className="fixed inset-0 pointer-events-none z-30 flex flex-col justify-between p-6 sm:p-10">
        {/* Top Minimal Navigation */}
        <header className="flex items-center justify-between w-full pointer-events-auto">
          <div className="flex items-center gap-3">
            <button
              onClick={() => scrollToScene(0)}
              className="group flex items-center gap-2 text-left"
            >
              <span className="font-editorial text-2xl sm:text-3xl tracking-widest text-[#C5F5D5] hover:opacity-80 transition-opacity">
                VERITAS AI
              </span>
            </button>
          </div>

          <nav className="flex items-center gap-2 sm:gap-6 text-[11px] sm:text-xs font-mono tracking-widest uppercase text-[#8A9B91]">
            <button
              onClick={() => scrollToScene(1)}
              className={`hover:text-[#C5F5D5] transition-colors py-1 px-2 ${
                currentSceneIdx === 1 ? 'text-[#C5F5D5]' : ''
              }`}
            >
              The Platform
            </button>
            <button
              onClick={() => scrollToScene(2)}
              className={`hover:text-[#C5F5D5] transition-colors py-1 px-2 ${
                currentSceneIdx === 2 || currentSceneIdx === 3 ? 'text-[#C5F5D5]' : ''
              }`}
            >
              The Intelligence
            </button>
            <button
              onClick={onOpenPricing}
              className="hover:text-[#C5F5D5] transition-colors py-1 px-2"
            >
              Pricing
            </button>
            <button
              onClick={onLoadDemo}
              className="hidden md:inline-block py-1.5 px-3.5 rounded-full border border-[rgba(197,245,213,0.18)] hover:border-[#C5F5D5] text-[#C5F5D5] hover:bg-[#101512] transition-all"
            >
              Explore Demo
            </button>
            {isAuthenticated ? (
              <button
                onClick={onLaunchWorkspace}
                className="py-1.5 px-4 rounded-full bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] font-semibold transition-all shadow-lg shadow-[#C5F5D5]/10 flex items-center gap-1.5"
              >
                <span>Workspace</span>
              </button>
            ) : (
              <div className="flex items-center gap-2">
                <button
                  onClick={() => openAuthModal('login')}
                  className="hidden sm:inline-block py-1.5 px-3 text-[#8A9B91] hover:text-[#F2F5F0] transition-colors"
                >
                  Sign In
                </button>
                <button
                  onClick={onLaunchWorkspace}
                  className="py-1.5 px-4 rounded-full bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] font-semibold transition-all shadow-lg shadow-[#C5F5D5]/10"
                >
                  Enter
                </button>
              </div>
            )}
          </nav>
        </header>

        {/* Peripheral Data Tags & Minimal HUD */}
        <div className="hidden lg:flex items-center justify-between text-[10px] font-mono tracking-widest text-[#8A9B91]/70 uppercase">
          <div>[ 52.3676° N, 4.9041° E ]</div>
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-[#C5F5D5] animate-pulse" />
            <span>ORIGIN: LIVE PROVENANCE · GEMINI FLASH</span>
          </div>
          <div>SCROLL PROGRESS // {(scrollProgress * 100).toFixed(0)}%</div>
        </div>

        {/* Bottom Status & Scroll Indicator */}
        <footer className="flex items-center justify-between w-full pointer-events-auto text-[11px] font-mono tracking-widest text-[#8A9B91]">
          <div className="flex items-center gap-3">
            <span className="text-[#C5F5D5]">0{currentSceneIdx + 1}</span>
            <span className="opacity-40">/</span>
            <span>05</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="hidden sm:inline-block text-[10px] tracking-widest uppercase opacity-60">
              Scroll to explore
            </span>
            <div className="w-4 h-6 rounded-full border border-[rgba(197,245,213,0.25)] flex items-start justify-center p-1">
              <div
                className="w-1 h-1 rounded-full bg-[#C5F5D5]"
                style={{
                  transform: `translateY(${Math.min(scrollProgress * 10, 10)}px)`,
                }}
              />
            </div>
          </div>
        </footer>
      </div>

      {/* Fixed Fullscreen Viewport for the 5 Scenes */}
      <div className="fixed inset-0 pointer-events-none z-20 flex items-center justify-center overflow-hidden">
        {/* =========================================================
            SCENE 1 — HERO
            ========================================================= */}
        <section
          style={getSceneStyle(0)}
          className="absolute inset-0 flex flex-col items-center justify-center text-center px-6"
        >
          <div className="max-w-4xl space-y-6">
            <div className="text-[11px] font-mono tracking-widest text-[#8A9B91] uppercase">
              VERITAS AI // CONTRACT INTELLIGENCE
            </div>

            <h1 className="font-editorial text-5xl sm:text-7xl md:text-8xl lg:text-9xl font-light text-[#C5F5D5] leading-[0.95] tracking-tight mint-glow">
              EVERY CLAUSE<br />
              HAS A STORY.
            </h1>

            <p className="font-sans text-sm sm:text-base text-[#8A9B91] max-w-md mx-auto pt-4 font-light leading-relaxed">
              Evidence-grounded intelligence for commercial agreements that matter.
            </p>

            <div className="pt-8 flex items-center justify-center gap-4">
              <button
                onClick={onLaunchWorkspace}
                className="py-3 px-8 rounded-full bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] font-medium text-xs sm:text-sm tracking-wider uppercase transition-all shadow-lg shadow-[#C5F5D5]/15"
              >
                Enter Veritas AI
              </button>
              <button
                onClick={() => scrollToScene(1)}
                className="py-3 px-6 rounded-full border border-[rgba(197,245,213,0.2)] hover:border-[#C5F5D5] text-[#C5F5D5] font-medium text-xs sm:text-sm tracking-wider uppercase transition-all"
              >
                The Architecture
              </button>
            </div>
          </div>
        </section>

        {/* =========================================================
            SCENE 2 — COMPLEXITY
            ========================================================= */}
        <section
          style={getSceneStyle(1)}
          className="absolute inset-0 flex flex-col items-center justify-center text-center px-6"
        >
          <div className="max-w-4xl space-y-6">
            <div className="text-[11px] font-mono tracking-widest text-[#8A9B91] uppercase">
              02 // THE FRICTION
            </div>

            <h2 className="font-editorial text-5xl sm:text-7xl md:text-8xl lg:text-9xl font-light text-[#C5F5D5] leading-[0.95] tracking-tight mint-glow">
              COMPLEXITY<br />
              HAS A COST.
            </h2>

            <p className="font-sans text-sm sm:text-base text-[#8A9B91] max-w-lg mx-auto pt-4 font-light leading-relaxed">
              Contracts contain obligations, risks, and critical decisions hidden across hundreds of non-standard clauses.
            </p>

            <div className="pt-4 grid grid-cols-2 sm:grid-cols-3 gap-6 text-left max-w-lg mx-auto text-xs font-mono text-[#8A9B91]/80">
              <div className="p-3 border border-[rgba(197,245,213,0.1)] rounded-lg">
                <div className="text-[#C5F5D5] font-bold text-sm">30+ Pages</div>
                <div className="mt-1 text-[10px]">Unstructured dense text</div>
              </div>
              <div className="p-3 border border-[rgba(197,245,213,0.1)] rounded-lg">
                <div className="text-[#FB923C] font-bold text-sm">Hidden Caps</div>
                <div className="mt-1 text-[10px]">Asymmetrical liabilities</div>
              </div>
              <div className="p-3 border border-[rgba(197,245,213,0.1)] rounded-lg col-span-2 sm:col-span-1">
                <div className="text-[#F87171] font-bold text-sm">Zero Audit</div>
                <div className="mt-1 text-[10px]">Hallucination vulnerability</div>
              </div>
            </div>
          </div>
        </section>

        {/* =========================================================
            SCENE 3 — TRANSFORMATION
            ========================================================= */}
        <section
          style={getSceneStyle(2)}
          className="absolute inset-0 flex flex-col items-center justify-center text-center px-6"
        >
          <div className="max-w-4xl space-y-6">
            <div className="text-[11px] font-mono tracking-widest text-[#8A9B91] uppercase">
              03 // THE TRANSFORMATION
            </div>

            <h2 className="font-editorial text-5xl sm:text-7xl md:text-8xl lg:text-9xl font-light text-[#C5F5D5] leading-[0.95] tracking-tight mint-glow">
              FROM CHAOS<br />
              TO CLARITY.
            </h2>

            <p className="font-sans text-sm sm:text-base text-[#8A9B91] max-w-lg mx-auto pt-4 font-light leading-relaxed">
              VERITAS AI connects raw contractual language directly with your organizational policies, benchmarks, and operational commitments.
            </p>

            <div className="pt-6 flex items-center justify-center gap-3 text-xs font-mono text-[#C5F5D5]">
              <span className="px-3 py-1 rounded-full border border-[rgba(197,245,213,0.2)] bg-[#101512]">
                Ollama Vector Embeddings
              </span>
              <span className="text-[#8A9B91]">→</span>
              <span className="px-3 py-1 rounded-full border border-[rgba(197,245,213,0.2)] bg-[#101512]">
                Playbook Alignment
              </span>
            </div>
          </div>
        </section>

        {/* =========================================================
            SCENE 4 — EVIDENCE
            ========================================================= */}
        <section
          style={getSceneStyle(3)}
          className="absolute inset-0 flex flex-col items-center justify-center text-center px-6"
        >
          <div className="max-w-5xl space-y-8">
            <div className="text-[11px] font-mono tracking-widest text-[#8A9B91] uppercase">
              04 // THE TRIPARTITE PROVENANCE
            </div>

            <h2 className="font-editorial text-5xl sm:text-7xl md:text-8xl lg:text-9xl font-light text-[#C5F5D5] leading-[0.95] tracking-tight mint-glow">
              TRUST IS BUILT<br />
              ON EVIDENCE.
            </h2>

            <p className="font-sans text-sm sm:text-base text-[#8A9B91] max-w-xl mx-auto font-light leading-relaxed">
              Every supported finding is verified against its source clause and relevant corporate policy requirement.
            </p>

            {/* The 3 visually connected formations */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4 max-w-3xl mx-auto text-left">
              <div className="p-5 rounded-xl border border-[rgba(197,245,213,0.15)] bg-[#101512]/90 backdrop-blur-md">
                <div className="text-[10px] font-mono text-[#8A9B91]">FORMATION A</div>
                <div className="font-editorial text-xl text-[#C5F5D5] mt-1">Contract Clause</div>
                <p className="text-xs text-[#8A9B91] mt-2 font-sans leading-relaxed">
                  Exact PyMuPDF token offsets and verbatim page text citations.
                </p>
              </div>

              <div className="p-5 rounded-xl border border-[rgba(197,245,213,0.15)] bg-[#101512]/90 backdrop-blur-md">
                <div className="text-[10px] font-mono text-[#8A9B91]">FORMATION B</div>
                <div className="font-editorial text-xl text-[#A8E6BF] mt-1">Company Policy</div>
                <p className="text-xs text-[#8A9B91] mt-2 font-sans leading-relaxed">
                  Corporate playbook standards and compliance thresholds.
                </p>
              </div>

              <div className="p-5 rounded-xl border border-[rgba(197,245,213,0.15)] bg-[#101512]/90 backdrop-blur-md">
                <div className="text-[10px] font-mono text-[#8A9B91]">FORMATION C</div>
                <div className="font-editorial text-xl text-[#C5F5D5] mt-1">Verified Finding</div>
                <p className="text-xs text-[#8A9B91] mt-2 font-sans leading-relaxed">
                  Deterministic quote check ensures zero synthetic hallucinations.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* =========================================================
            SCENE 5 — FINALE
            ========================================================= */}
        <section
          style={getSceneStyle(4)}
          className="absolute inset-0 flex flex-col items-center justify-center text-center px-6"
        >
          <div className="max-w-4xl space-y-8">
            <div className="text-[11px] font-mono tracking-widest text-[#8A9B91] uppercase">
              05 // THE WORKSPACE
            </div>

            <h2 className="font-editorial text-5xl sm:text-7xl md:text-8xl lg:text-9xl font-light text-[#C5F5D5] leading-[0.95] tracking-tight mint-glow">
              INTELLIGENCE<br />
              YOU CAN TRACE.
            </h2>

            <p className="font-sans text-sm sm:text-base text-[#8A9B91] max-w-md mx-auto font-light leading-relaxed">
              Launch the full analytical workspace. Inspect live findings, operational obligations, and deterministic graphs.
            </p>

            <div className="pt-6 flex flex-wrap items-center justify-center gap-4">
              <button
                onClick={onLaunchWorkspace}
                className="py-4 px-10 rounded-full bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] font-semibold text-xs sm:text-sm tracking-widest uppercase transition-all shadow-xl shadow-[#C5F5D5]/20 hover:scale-105 active:scale-95"
              >
                Enter Veritas AI
              </button>
              <button
                onClick={onLoadDemo}
                className="py-4 px-8 rounded-full border border-[rgba(197,245,213,0.3)] hover:border-[#C5F5D5] text-[#C5F5D5] hover:bg-[#101512] font-semibold text-xs sm:text-sm tracking-widest uppercase transition-all hover:scale-105 active:scale-95"
              >
                Explore Demo
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
