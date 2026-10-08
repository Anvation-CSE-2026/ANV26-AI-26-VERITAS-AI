import React from 'react'
import {
  IconShield,
  IconDocument,
  IconCheckCircle,
  IconSparkles,
} from '../icons/Icons'

export default function CompanyWorkspaceView({ onSwitchToContracts, onOpenDemo }) {
  return (
    <div className="space-y-10 text-left pb-12 max-w-6xl mx-auto">
      {/* 1. HERO SECTION */}
      <div className="space-y-4">
        <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full border border-[#C5F5D5]/30 bg-[#101512] text-[#C5F5D5] text-xs font-sans">
          <span className="w-2 h-2 rounded-full bg-[#C5F5D5] animate-pulse" />
          <span className="font-semibold tracking-wider uppercase">ENTERPRISE ROADMAP</span>
          <span className="text-[#8A9B91]">· Coming Soon</span>
        </div>

        <div>
          <h1 className="font-editorial text-4xl sm:text-5xl lg:text-6xl font-light text-[#F2F5F0] tracking-tight">
            COMPANY WORKSPACE.
          </h1>
          <p className="font-sans text-base sm:text-lg text-[#8A9B91] mt-2 max-w-3xl leading-relaxed">
            Enterprise contract intelligence powered by your organization's custom legal playbooks and multi-tenant isolation.
          </p>
        </div>
      </div>

      {/* 2. CURRENT BACKEND STATUS & HONEST DISCLOSURE */}
      <div className="p-6 sm:p-8 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.15)] space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.2)] text-[#C5F5D5] flex items-center justify-center">
            <IconShield className="w-5 h-5 text-[#C5F5D5]" />
          </div>
          <div>
            <h3 className="font-sans text-lg font-semibold text-[#F2F5F0]">
              Current Policy Configuration
            </h3>
            <p className="text-xs text-[#8A9B91] font-sans">
              How VERITAS AI currently evaluates contracts in this environment
            </p>
          </div>
        </div>

        <p className="text-sm font-sans text-[#F2F5F0] leading-relaxed">
          The current backend evaluates all contracts against the built-in{' '}
          <strong className="text-[#C5F5D5]">Standard Commercial Agreement Playbook (v1.0)</strong>,
          covering core commercial categories: Liability Caps, Third-Party Indemnification, Termination for Convenience,
          Mutual Confidentiality, Net 30 Payment, 48-Hour Data Breach Notification, and Intellectual Property Ownership.
        </p>

        <div className="p-4 rounded-xl bg-[#080B0A] border border-white/5 text-xs text-[#8A9B91] font-sans space-y-2">
          <span className="font-semibold text-[#C5F5D5] uppercase tracking-wider text-[11px] block">
            TRANSPARENCY NOTICE
          </span>
          <p>
            The backend does not currently support arbitrary tenant policy uploads, organization account isolation, or multi-tenant database partitioning. We do not simulate or fake custom policy uploads.
          </p>
        </div>
      </div>

      {/* 3. UPCOMING ENTERPRISE CAPABILITIES */}
      <div className="space-y-4">
        <h2 className="font-editorial text-3xl font-light text-[#F2F5F0]">
          UPCOMING ENTERPRISE FEATURES
        </h2>
        <p className="text-sm text-[#8A9B91] font-sans">
          Capabilities scheduled for organizational deployment:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
          {/* Feature 1 */}
          <div className="p-6 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.1)] space-y-3">
            <div className="flex items-center gap-2 text-xs font-sans text-[#C5F5D5] font-semibold uppercase tracking-wider">
              <IconDocument className="w-4 h-4 text-[#C5F5D5]" />
              <span>Custom Policy Ingestion</span>
            </div>
            <h3 className="font-sans text-lg font-semibold text-[#F2F5F0]">
              Upload Your Own Legal Playbook
            </h3>
            <p className="text-sm text-[#8A9B91] font-sans leading-relaxed">
              Upload your company's proprietary legal standards via PDF or structured schema. Tailor standard clauses, acceptable fallbacks, and non-negotiables for your business.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="p-6 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.1)] space-y-3">
            <div className="flex items-center gap-2 text-xs font-sans text-[#A8E6BF] font-semibold uppercase tracking-wider">
              <IconShield className="w-4 h-4 text-[#A8E6BF]" />
              <span>Multi-Tenant Isolation</span>
            </div>
            <h3 className="font-sans text-lg font-semibold text-[#F2F5F0]">
              Organization & Team Accounts
            </h3>
            <p className="text-sm text-[#8A9B91] font-sans leading-relaxed">
              Encrypted, tenant-partitioned SQLite / PostgreSQL storage with role-based access control for Legal, Procurement, and Executive reviewers.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="p-6 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.1)] space-y-3">
            <div className="flex items-center gap-2 text-xs font-sans text-[#FDE047] font-semibold uppercase tracking-wider">
              <IconSparkles className="w-4 h-4 text-[#FDE047]" />
              <span>Deal-Specific Risk Thresholds</span>
            </div>
            <h3 className="font-sans text-lg font-semibold text-[#F2F5F0]">
              Configurable Risk Sensitivity
            </h3>
            <p className="text-sm text-[#8A9B91] font-sans leading-relaxed">
              Tune severity triggers based on vendor tiers, transaction size, and jurisdiction to prioritize risks that matter most for each business transaction.
            </p>
          </div>

          {/* Feature 4 */}
          <div className="p-6 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.1)] space-y-3">
            <div className="flex items-center gap-2 text-xs font-sans text-[#C5F5D5] font-semibold uppercase tracking-wider">
              <IconCheckCircle className="w-4 h-4 text-[#C5F5D5]" />
              <span>Audit & Compliance Reporting</span>
            </div>
            <h3 className="font-sans text-lg font-semibold text-[#F2F5F0]">
              Enterprise Audit Trails
            </h3>
            <p className="text-sm text-[#8A9B91] font-sans leading-relaxed">
              Generate executive compliance reports and auditable provenance trails showing exact clause quotes, token offsets, and qualified legal reviewer sign-offs.
            </p>
          </div>
        </div>
      </div>

      {/* 4. TECHNICAL ARCHITECTURE ROADMAP */}
      <div className="p-6 sm:p-8 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] space-y-4">
        <h3 className="font-editorial text-2xl text-[#F2F5F0]">
          Backend Architecture Roadmap
        </h3>
        <p className="text-xs text-[#8A9B91] font-sans">
          Required engineering components for production enterprise deployment:
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 text-xs font-mono">
          <div className="p-4 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.08)] space-y-1">
            <span className="text-[#C5F5D5] font-bold">1. Playbook Ingestion API</span>
            <p className="text-[#8A9B91] font-sans">
              `POST /api/playbooks/upload` to validate and persist custom rule schemas.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.08)] space-y-1">
            <span className="text-[#A8E6BF] font-bold">2. Tenant Vector Collections</span>
            <p className="text-[#8A9B91] font-sans">
              Partitioned vector embeddings in Ollama/Qdrant per organization namespace.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.08)] space-y-1">
            <span className="text-[#FDE047] font-bold">3. Database Multi-Tenancy</span>
            <p className="text-[#8A9B91] font-sans">
              Organization-scoped foreign keys and tenant isolation in database tables.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.08)] space-y-1">
            <span className="text-[#C5F5D5] font-bold">4. Auth & Role-Based Access</span>
            <p className="text-[#8A9B91] font-sans">
              JWT authentication, legal counsel permissions, and audit log generation.
            </p>
          </div>
        </div>
      </div>

      {/* 5. CTAs */}
      <div className="p-8 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.15)] flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <h3 className="font-editorial text-2xl text-[#F2F5F0]">
            Ready to test standard contract analysis?
          </h3>
          <p className="text-xs text-[#8A9B91] font-sans mt-0.5">
            Analyze a real contract with our built-in commercial policy, or explore the verified demo.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={onSwitchToContracts}
            className="px-6 py-2.5 rounded-full bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] text-xs font-sans font-semibold tracking-wide transition-all shadow-md shadow-[#C5F5D5]/10"
          >
            Upload Contract
          </button>
          <button
            onClick={onOpenDemo}
            className="px-6 py-2.5 rounded-full border border-[rgba(197,245,213,0.25)] hover:border-[#C5F5D5] text-[#C5F5D5] text-xs font-sans font-medium tracking-wide transition-all"
          >
            Explore Demo
          </button>
        </div>
      </div>
    </div>
  )
}
