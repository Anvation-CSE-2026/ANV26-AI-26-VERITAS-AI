import React, { useState, useMemo, useCallback } from 'react'
import {
  ReactFlow,
  ReactFlowProvider,
  Background,
  Controls,
  Handle,
  Position,
  MarkerType,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import dagre from 'dagre'
import {
  IconGraph,
  IconSearch,
  IconArrowRight,
  IconDocument,
  IconShield,
  IconScale,
  IconClock,
  IconCheckCircle,
  IconSparkles,
} from '../icons/Icons'
import { RISK_LEVELS, CLAUSE_CATEGORIES } from '../../types/constants'

// Custom Entity Node Component for React Flow
function CustomEntityNode({ data, selected }) {
  const { label, subtext, count, badge, color, iconType, isRoot } = data

  const getBorderColor = () => {
    if (selected) return '#C5F5D5'
    if (color) return color
    return 'rgba(197, 245, 213, 0.2)'
  }

  const renderIcon = () => {
    switch (iconType) {
      case 'contract':
        return <IconDocument className="w-4 h-4 text-[#C5F5D5]" />
      case 'policy':
        return <IconShield className="w-4 h-4 text-[#A8E6BF]" />
      case 'finding':
        return <IconScale className="w-4 h-4 text-[#FB923C]" />
      case 'action':
        return <IconSparkles className="w-4 h-4 text-[#C5F5D5]" />
      case 'obligation':
        return <IconClock className="w-4 h-4 text-[#C5F5D5]" />
      default:
        return <IconGraph className="w-4 h-4 text-[#C5F5D5]" />
    }
  }

  return (
    <div
      className={`px-4 py-3 rounded-xl border text-left transition-all min-w-[210px] max-w-[260px] cursor-pointer shadow-lg ${
        selected
          ? 'bg-[#15231B] ring-2 ring-[#C5F5D5] shadow-[#C5F5D5]/20 scale-105'
          : 'bg-[#101512] hover:bg-[#151D18]'
      }`}
      style={{
        borderColor: getBorderColor(),
        borderWidth: isRoot ? '2px' : '1px',
      }}
    >
      {/* Horizontal Handles for clean Left-to-Right diagram routing */}
      <Handle
        type="target"
        position={Position.Left}
        className="!w-2 !h-2 !bg-[#C5F5D5] !border-none"
      />
      <Handle
        type="source"
        position={Position.Right}
        className="!w-2 !h-2 !bg-[#C5F5D5] !border-none"
      />

      <div className="flex items-center justify-between gap-2 mb-1">
        <div className="flex items-center gap-1.5 text-xs font-sans font-medium text-[#8A9B91]">
          {renderIcon()}
          <span className="uppercase tracking-wider text-[10px]">{subtext || 'Entity'}</span>
        </div>

        {badge && (
          <span
            className="px-2 py-0.5 rounded text-[10px] font-sans font-semibold border"
            style={{
              borderColor: `${color || '#C5F5D5'}40`,
              color: color || '#C5F5D5',
              backgroundColor: `${color || '#C5F5D5'}15`,
            }}
          >
            {badge}
          </span>
        )}

        {typeof count === 'number' && (
          <span
            className="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-mono font-bold"
            style={{
              backgroundColor: `${color || '#C5F5D5'}25`,
              color: color || '#C5F5D5',
            }}
          >
            {count}
          </span>
        )}
      </div>

      <div className="font-sans font-medium text-sm text-[#F2F5F0] truncate" title={label}>
        {label}
      </div>
    </div>
  )
}

const nodeTypes = {
  entity: CustomEntityNode,
}

// Dagre Layout Engine
function getLayoutedElements(nodes, edges, direction = 'LR') {
  const dagreGraph = new dagre.graphlib.Graph()
  dagreGraph.setDefaultEdgeLabel(() => ({}))

  const isHorizontal = direction === 'LR'
  dagreGraph.setGraph({
    rankdir: direction,
    nodesep: 40,
    ranksep: 90,
  })

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: 230, height: 75 })
  })

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target)
  })

  dagre.layout(dagreGraph)

  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id)
    return {
      ...node,
      targetPosition: isHorizontal ? Position.Left : Position.Top,
      sourcePosition: isHorizontal ? Position.Right : Position.Bottom,
      position: {
        x: nodeWithPosition.x - 115,
        y: nodeWithPosition.y - 37.5,
      },
    }
  })

  return { displayNodes: layoutedNodes, displayEdges: edges }
}

export default function KnowledgeGraphView({
  analysis,
  contract,
  onNavigateToFinding,
  onOpenUpload,
  onLoadDemo,
}) {
  // Default to FOCUSED view as mandated
  const [viewMode, setViewMode] = useState('focused')
  const [selectedFindingIndex, setSelectedFindingIndex] = useState(0)
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [selectedNodeData, setSelectedNodeData] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [fullCategoryFilter, setFullCategoryFilter] = useState('all')

  const findings = useMemo(() => analysis?.findings || [], [analysis])
  const obligations = useMemo(() => analysis?.obligations || [], [analysis])

  const currentFinding = findings[selectedFindingIndex] || findings[0]

  // BUILD GRAPH DATA ACCORDING TO CURRENT VIEW MODE
  const { displayNodes, displayEdges } = useMemo(() => {
    if (!analysis) return { displayNodes: [], displayEdges: [] }

    const contractId = 'contract-root'
    const contractLabel = contract?.filename || 'Contract Agreement'

    // ==========================================
    // 1. FOCUSED MODE (DEFAULT: 4-Card Cause-and-Effect Chain)
    // CONTRACT CLAUSE -> COMPANY POLICY -> IDENTIFIED RISK -> RECOMMENDED ACTION
    // ==========================================
    if (viewMode === 'focused' && currentFinding) {
      const riskConfig = RISK_LEVELS[currentFinding.risk_level] || RISK_LEVELS.medium
      const categoryLabel =
        CLAUSE_CATEGORIES[currentFinding.clause_category] || currentFinding.clause_category

      const clauseNodeId = `focused-clause-${currentFinding.clause_id || 'omission'}`
      const policyNodeId = `focused-policy-${currentFinding.policy_id}`
      const riskNodeId = `focused-risk-${selectedFindingIndex}`
      const actionNodeId = `focused-action-${selectedFindingIndex}`

      const rawNodes = [
        {
          id: clauseNodeId,
          type: 'entity',
          data: {
            label: currentFinding.clause_id
              ? `Clause ${currentFinding.clause_id}`
              : 'Contract Clause (Omission)',
            subtext: '1. Contract Clause',
            badge: currentFinding.page_number ? `Page ${currentFinding.page_number}` : 'Omission',
            color: '#C5F5D5',
            iconType: 'contract',
          },
          position: { x: 0, y: 0 },
        },
        {
          id: policyNodeId,
          type: 'entity',
          data: {
            label: `Rule ${currentFinding.policy_id}`,
            subtext: '2. Company Policy',
            badge: categoryLabel,
            color: '#A8E6BF',
            iconType: 'policy',
          },
          position: { x: 0, y: 0 },
        },
        {
          id: riskNodeId,
          type: 'entity',
          data: {
            label: `${categoryLabel} Deviation`,
            subtext: '3. Identified Risk',
            badge: riskConfig.label,
            color: riskConfig.color,
            iconType: 'finding',
            finding: currentFinding,
          },
          position: { x: 0, y: 0 },
        },
        {
          id: actionNodeId,
          type: 'entity',
          data: {
            label: currentFinding.recommended_action
              ? 'Required Remediation'
              : 'Legal Review',
            subtext: '4. Recommended Action',
            badge: 'ACTION',
            color: '#C5F5D5',
            iconType: 'action',
            finding: currentFinding,
          },
          position: { x: 0, y: 0 },
        },
      ]

      const rawEdges = [
        {
          id: 'e-clause-policy',
          source: clauseNodeId,
          target: policyNodeId,
          label: 'evaluated against',
          animated: true,
          style: { stroke: '#A8E6BF', strokeWidth: 2 },
          labelStyle: { fill: '#8A9B91', fontSize: 10, fontFamily: 'sans-serif' },
          markerEnd: { type: MarkerType.ArrowClosed, color: '#A8E6BF' },
        },
        {
          id: 'e-policy-risk',
          source: policyNodeId,
          target: riskNodeId,
          label: 'conflict detected',
          animated: true,
          style: { stroke: riskConfig.color, strokeWidth: 2 },
          labelStyle: { fill: '#8A9B91', fontSize: 10, fontFamily: 'sans-serif' },
          markerEnd: { type: MarkerType.ArrowClosed, color: riskConfig.color },
        },
        {
          id: 'e-risk-action',
          source: riskNodeId,
          target: actionNodeId,
          label: 'mitigated by',
          animated: true,
          style: { stroke: '#C5F5D5', strokeWidth: 2 },
          labelStyle: { fill: '#8A9B91', fontSize: 10, fontFamily: 'sans-serif' },
          markerEnd: { type: MarkerType.ArrowClosed, color: '#C5F5D5' },
        },
      ]

      return getLayoutedElements(rawNodes, rawEdges, 'LR')
    }

    // ==========================================
    // 2. CATEGORY MAP (Tree/Grouped Layout)
    // Central Node: Contract -> Branch Nodes: Categories -> Leaf Nodes: Findings
    // ==========================================
    if (viewMode === 'category') {
      const rawNodes = [
        {
          id: contractId,
          type: 'entity',
          data: {
            label: contractLabel,
            subtext: 'Central Agreement',
            isRoot: true,
            color: '#C5F5D5',
            iconType: 'contract',
          },
          position: { x: 0, y: 0 },
        },
      ]
      const rawEdges = []

      // Group findings by category
      const categoriesPresent = new Set()
      findings.forEach((f) => {
        if (f.clause_category) categoriesPresent.add(f.clause_category)
      })

      categoriesPresent.forEach((cat) => {
        const catFindings = findings.filter((f) => f.clause_category === cat)
        const catNodeId = `cat-node-${cat}`
        const catLabel = CLAUSE_CATEGORIES[cat] || cat
        const isCatSelected = selectedCategory === cat

        // Determine highest severity in this category
        const hasCritical = catFindings.some((f) => f.risk_level === 'critical')
        const hasHigh = catFindings.some((f) => f.risk_level === 'high')
        const catColor = hasCritical ? '#F87171' : hasHigh ? '#FB923C' : '#FDE047'

        rawNodes.push({
          id: catNodeId,
          type: 'entity',
          data: {
            label: catLabel,
            subtext: 'Risk Category',
            count: catFindings.length,
            badge: `${catFindings.length} Finding${catFindings.length > 1 ? 's' : ''}`,
            color: catColor,
            iconType: 'finding',
            categoryKey: cat,
          },
          position: { x: 0, y: 0 },
        })

        rawEdges.push({
          id: `e-contract-${catNodeId}`,
          source: contractId,
          target: catNodeId,
          style: { stroke: `${catColor}80`, strokeWidth: 2 },
          markerEnd: { type: MarkerType.ArrowClosed, color: catColor },
        })

        // If no specific category selected OR this category is selected, render leaves
        if (!selectedCategory || isCatSelected) {
          catFindings.forEach((f, idx) => {
            const riskConfig = RISK_LEVELS[f.risk_level] || RISK_LEVELS.medium
            const leafNodeId = `leaf-finding-${cat}-${idx}`

            rawNodes.push({
              id: leafNodeId,
              type: 'entity',
              data: {
                label: f.clause_id ? `Clause ${f.clause_id}` : 'Omission',
                subtext: f.policy_id,
                badge: riskConfig.label,
                color: riskConfig.color,
                iconType: 'finding',
                finding: f,
              },
              position: { x: 0, y: 0 },
            })

            rawEdges.push({
              id: `e-${catNodeId}-${leafNodeId}`,
              source: catNodeId,
              target: leafNodeId,
              style: { stroke: riskConfig.color, strokeWidth: 1.5 },
              markerEnd: { type: MarkerType.ArrowClosed, color: riskConfig.color },
            })
          })
        }
      })

      return getLayoutedElements(rawNodes, rawEdges, 'LR')
    }

    // ==========================================
    // 3. FULL NETWORK MODE (Hierarchical Power Graph)
    // ==========================================
    const rawNodes = []
    const rawEdges = []

    // 1. Root Contract
    rawNodes.push({
      id: contractId,
      type: 'entity',
      data: {
        label: contractLabel,
        subtext: 'Root Document',
        isRoot: true,
        color: '#C5F5D5',
        iconType: 'contract',
      },
      position: { x: 0, y: 0 },
    })

    // 2. Unique Clauses
    const clauseMap = new Map()
    findings.forEach((f) => {
      if (f.clause_id && !clauseMap.has(f.clause_id)) {
        clauseMap.set(f.clause_id, f.page_number)
      }
    })
    obligations.forEach((o) => {
      if (o.clause_id && !clauseMap.has(o.clause_id)) {
        clauseMap.set(o.clause_id, o.page_number)
      }
    })

    clauseMap.forEach((page, cid) => {
      rawNodes.push({
        id: `clause-${cid}`,
        type: 'entity',
        data: {
          label: cid,
          subtext: 'Clause',
          badge: page ? `P${page}` : undefined,
          color: '#C5F5D5',
          iconType: 'contract',
        },
        position: { x: 0, y: 0 },
      })
      rawEdges.push({
        id: `e-doc-${cid}`,
        source: contractId,
        target: `clause-${cid}`,
        style: { stroke: 'rgba(197, 245, 213, 0.25)', strokeWidth: 1.5 },
      })
    })

    // 3. Policies
    const policyMap = new Map()
    findings.forEach((f) => {
      if (f.policy_id && !policyMap.has(f.policy_id)) {
        policyMap.set(f.policy_id, f.clause_category)
      }
    })

    policyMap.forEach((category, pid) => {
      rawNodes.push({
        id: `policy-${pid}`,
        type: 'entity',
        data: {
          label: pid,
          subtext: 'Policy Rule',
          badge: CLAUSE_CATEGORIES[category] || category,
          color: '#A8E6BF',
          iconType: 'policy',
        },
        position: { x: 0, y: 0 },
      })
    })

    // 4. Findings
    findings.forEach((f, idx) => {
      if (fullCategoryFilter !== 'all' && f.clause_category !== fullCategoryFilter) {
        return
      }
      if (searchQuery) {
        const q = searchQuery.toLowerCase()
        const matchesQuery =
          f.explanation.toLowerCase().includes(q) ||
          (f.clause_id && f.clause_id.toLowerCase().includes(q)) ||
          f.policy_id.toLowerCase().includes(q)
        if (!matchesQuery) return
      }
      const riskConfig = RISK_LEVELS[f.risk_level] || RISK_LEVELS.medium
      const fid = `finding-${idx}`

      rawNodes.push({
        id: fid,
        type: 'entity',
        data: {
          label: `${CLAUSE_CATEGORIES[f.clause_category] || f.clause_category}`,
          subtext: 'Finding',
          badge: riskConfig.label,
          color: riskConfig.color,
          iconType: 'finding',
          finding: f,
        },
        position: { x: 0, y: 0 },
      })

      if (f.clause_id && clauseMap.has(f.clause_id)) {
        rawEdges.push({
          id: `e-${f.clause_id}-${fid}`,
          source: `clause-${f.clause_id}`,
          target: fid,
          style: { stroke: riskConfig.color, strokeWidth: 1.5 },
        })
      }
      if (f.policy_id && policyMap.has(f.policy_id)) {
        rawEdges.push({
          id: `e-${f.policy_id}-${fid}`,
          source: `policy-${f.policy_id}`,
          target: fid,
          style: { stroke: '#A8E6BF', strokeWidth: 1.5 },
        })
      }
    })

    // 5. Obligations
    obligations.forEach((o, idx) => {
      const oid = `ob-${idx}`
      rawNodes.push({
        id: oid,
        type: 'entity',
        data: {
          label: o.responsible_party || 'Contract Duty',
          subtext: 'Obligation',
          badge: o.deadline ? `${o.deadline}` : 'Action',
          color: '#C5F5D5',
          iconType: 'obligation',
        },
        position: { x: 0, y: 0 },
      })

      if (o.clause_id && clauseMap.has(o.clause_id)) {
        rawEdges.push({
          id: `e-cl-${o.clause_id}-${oid}`,
          source: `clause-${o.clause_id}`,
          target: oid,
          style: { stroke: '#C5F5D5', strokeWidth: 1.5, strokeDasharray: '4,4' },
        })
      }
    })

    return getLayoutedElements(rawNodes, rawEdges, 'LR')
  }, [
    analysis,
    contract,
    viewMode,
    currentFinding,
    selectedFindingIndex,
    selectedCategory,
    findings,
    obligations,
    searchQuery,
    fullCategoryFilter,
  ])

  // Click Handler for Nodes
  const handleNodeClick = useCallback(
    (_, node) => {
      if (node.data) {
        setSelectedNodeData(node.data)
        if (node.data.categoryKey) {
          setSelectedCategory((prev) => (prev === node.data.categoryKey ? null : node.data.categoryKey))
        }
      }
    },
    []
  )

  if (!analysis) {
    return (
      <div className="p-16 text-center rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] text-[#8A9B91] space-y-4 max-w-xl mx-auto my-12">
        <IconGraph className="w-12 h-12 mx-auto text-[#C5F5D5] opacity-40" />
        <h4 className="font-editorial text-3xl font-light text-[#F2F5F0]">
          No Relationship Graph Loaded
        </h4>
        <p className="text-sm font-sans text-[#8A9B91] leading-relaxed">
          Upload an agreement or load the demo dataset to view deterministically derived connections.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
          {onOpenUpload && (
            <button
              onClick={onOpenUpload}
              className="px-6 py-2.5 rounded-full bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] text-xs font-sans font-semibold tracking-wide transition-all shadow-md"
            >
              Upload Contract
            </button>
          )}
          {onLoadDemo && (
            <button
              onClick={onLoadDemo}
              className="px-6 py-2.5 rounded-full border border-[rgba(197,245,213,0.25)] hover:border-[#C5F5D5] text-[#C5F5D5] text-xs font-sans tracking-wide transition-all"
            >
              Load Demo Data
            </button>
          )}
        </div>
      </div>
    )
  }

  // Active finding for inspector (either clicked finding or current focused finding)
  const inspectorFinding = selectedNodeData?.finding || currentFinding

  return (
    <div className="space-y-8 text-left pb-12">
      {/* 1. HEADER & MODE SWITCHER */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="font-editorial text-4xl sm:text-5xl lg:text-6xl font-light text-[#F2F5F0]">
            KNOWLEDGE GRAPH.
          </h1>
          <p className="font-sans text-base sm:text-lg text-[#8A9B91] mt-2 leading-relaxed max-w-2xl">
            Explore deterministically grounded relationships connecting contracts, policies, and findings.
          </p>
        </div>

        {/* 3 VIEW MODES SWITCHER */}
        <div className="flex items-center p-1 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.15)] gap-1">
          <button
            onClick={() => {
              setViewMode('focused')
              setSelectedNodeData(null)
            }}
            className={`px-4 py-2 rounded-xl text-xs font-sans font-semibold transition-all ${
              viewMode === 'focused'
                ? 'bg-[#15231B] text-[#C5F5D5] shadow-sm border border-[#C5F5D5]/30'
                : 'text-[#8A9B91] hover:text-[#F2F5F0]'
            }`}
          >
            FOCUSED VIEW
          </button>
          <button
            onClick={() => {
              setViewMode('category')
              setSelectedNodeData(null)
            }}
            className={`px-4 py-2 rounded-xl text-xs font-sans font-semibold transition-all ${
              viewMode === 'category'
                ? 'bg-[#15231B] text-[#C5F5D5] shadow-sm border border-[#C5F5D5]/30'
                : 'text-[#8A9B91] hover:text-[#F2F5F0]'
            }`}
          >
            CATEGORY MAP
          </button>
          <button
            onClick={() => {
              setViewMode('full')
              setSelectedNodeData(null)
            }}
            className={`px-4 py-2 rounded-xl text-xs font-sans font-semibold transition-all ${
              viewMode === 'full'
                ? 'bg-[#15231B] text-[#C5F5D5] shadow-sm border border-[#C5F5D5]/30'
                : 'text-[#8A9B91] hover:text-[#F2F5F0]'
            }`}
          >
            FULL NETWORK
          </button>
        </div>
      </div>

      {/* Mode Subtext / Quick Switcher for Focused Mode */}
      {viewMode === 'focused' && (
        <div className="space-y-2">
          <div className="text-xs font-sans text-[#8A9B91]">
            Step-by-step cause-and-effect chain for each identified contractual risk:
          </div>
          <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
            {findings.map((f, idx) => {
              const isSelected = idx === selectedFindingIndex
              const riskConfig = RISK_LEVELS[f.risk_level] || RISK_LEVELS.medium
              return (
                <button
                  key={idx}
                  onClick={() => {
                    setSelectedFindingIndex(idx)
                    setSelectedNodeData(null)
                  }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-sans whitespace-nowrap transition-all border shrink-0 flex items-center gap-1.5 ${
                    isSelected
                      ? 'bg-[#15231B] border-[#C5F5D5] text-[#C5F5D5] font-semibold'
                      : 'bg-[#101512] border-[rgba(197,245,213,0.1)] text-[#8A9B91] hover:text-[#F2F5F0]'
                  }`}
                >
                  <span className={`w-2 h-2 rounded-full ${riskConfig.bg}`} />
                  <span>{CLAUSE_CATEGORIES[f.clause_category] || f.clause_category}</span>
                  <span className="text-[10px] opacity-70">#{idx + 1}</span>
                </button>
              )
            })}
          </div>
        </div>
      )}

      {/* Mode Subtext / Category Filter for Category Map */}
      {viewMode === 'category' && (
        <div className="flex flex-wrap items-center gap-2 pb-1">
          <span className="text-xs font-sans text-[#8A9B91] mr-1">Filter Category:</span>
          <button
            onClick={() => setSelectedCategory(null)}
            className={`px-3 py-1 rounded-lg text-xs font-sans transition-all border ${
              !selectedCategory
                ? 'bg-[#15231B] text-[#C5F5D5] border-[#C5F5D5]/40 font-semibold'
                : 'bg-[#101512] text-[#8A9B91] border-white/5 hover:text-[#F2F5F0]'
            }`}
          >
            Show All
          </button>
          {Array.from(new Set(findings.map((f) => f.clause_category))).map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(selectedCategory === cat ? null : cat)}
              className={`px-3 py-1 rounded-lg text-xs font-sans transition-all border ${
                selectedCategory === cat
                  ? 'bg-[#15231B] text-[#C5F5D5] border-[#C5F5D5]/40 font-semibold'
                  : 'bg-[#101512] text-[#8A9B91] border-white/5 hover:text-[#F2F5F0]'
              }`}
            >
              {CLAUSE_CATEGORIES[cat] || cat}
            </button>
          ))}
        </div>
      )}

      {/* Mode Subtext / Filters for Full Network Mode */}
      {viewMode === 'full' && (
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2">
              <span className="text-xs font-sans text-[#8A9B91]">Category:</span>
              <select
                value={fullCategoryFilter}
                onChange={(e) => setFullCategoryFilter(e.target.value)}
                className="bg-[#101512] border border-[rgba(197,245,213,0.15)] text-[#F2F5F0] text-xs font-sans rounded-xl px-3 py-1.5 focus:outline-none focus:border-[#C5F5D5]"
              >
                <option value="all">All Categories</option>
                {Object.entries(CLAUSE_CATEGORIES).map(([key, label]) => (
                  <option key={key} value={key}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            {/* Visual Node Legend */}
            <div className="hidden xl:flex items-center gap-3 pl-4 border-l border-[rgba(197,245,213,0.1)] text-xs text-[#8A9B91]">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#C5F5D5]" /> Contract
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#A8E6BF]" /> Policy
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#FB923C]" /> Risk
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#C5F5D5]" /> Action
              </span>
            </div>
          </div>

          {/* Search Nodes */}
          <div className="relative">
            <input
              type="text"
              placeholder="Filter graph nodes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-[#101512] border border-[rgba(197,245,213,0.15)] rounded-xl px-3.5 py-1.5 text-xs text-[#F2F5F0] placeholder-[#8A9B91] focus:outline-none focus:border-[#C5F5D5] w-52 font-sans"
            />
            <IconSearch className="w-3.5 h-3.5 text-[#8A9B91] absolute right-3 top-2.5 pointer-events-none" />
          </div>
        </div>
      )}

      {/* 2. GRAPH CANVAS & DETAIL PANEL */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* REACT FLOW GRAPH CANVAS (7 or 8 cols) */}
        <div className="lg:col-span-7 xl:col-span-8 rounded-2xl bg-[#080B0A] border border-[rgba(197,245,213,0.12)] overflow-hidden h-[540px] relative shadow-lg">
          <ReactFlowProvider>
            <ReactFlow
              nodes={displayNodes}
              edges={displayEdges}
              nodeTypes={nodeTypes}
              onNodeClick={handleNodeClick}
              fitView
              fitViewOptions={{ padding: 0.2 }}
              minZoom={0.2}
              maxZoom={1.5}
              proOptions={{ hideAttribution: true }}
            >
              <Background color="#15231B" gap={20} size={1} />
              <Controls
                position="bottom-right"
                className="!bg-[#101512] !border-[rgba(197,245,213,0.15)] !rounded-xl !overflow-hidden [&>button]:!bg-[#101512] [&>button]:!border-b-[rgba(197,245,213,0.1)] [&>button]:!fill-[#C5F5D5]"
              />
            </ReactFlow>
          </ReactFlowProvider>

          {/* Mode Watermark */}
          <div className="absolute top-4 left-4 z-10 pointer-events-none">
            <span className="text-[11px] font-mono tracking-wider text-[#8A9B91]/80 bg-[#101512]/90 backdrop-blur-md px-3 py-1 rounded-full border border-[rgba(197,245,213,0.1)]">
              {viewMode === 'focused'
                ? 'Focused: 4-Stage Cause-and-Effect Chain'
                : viewMode === 'category'
                ? 'Category Map: Grouped Hierarchy'
                : 'Full Network: Grounded Knowledge Graph'}
            </span>
          </div>
        </div>

        {/* NODE INSPECTOR DRAWER / EXPLANATION PANEL (5 or 4 cols) */}
        <div className="lg:col-span-5 xl:col-span-4 p-6 sm:p-7 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] flex flex-col justify-between space-y-6 shadow-sm">
          {inspectorFinding ? (
            <div className="space-y-5">
              {/* Header */}
              <div className="pb-4 border-b border-[rgba(197,245,213,0.1)] space-y-2">
                <div className="flex items-center gap-2">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-sans font-semibold ${
                      (RISK_LEVELS[inspectorFinding.risk_level] || RISK_LEVELS.medium).badgeClass
                    }`}
                  >
                    {(RISK_LEVELS[inspectorFinding.risk_level] || RISK_LEVELS.medium).label}
                  </span>
                  <span className="text-xs font-sans text-[#8A9B91]">
                    {CLAUSE_CATEGORIES[inspectorFinding.clause_category] || inspectorFinding.clause_category}
                  </span>
                </div>
                <h3 className="font-editorial text-2xl font-light text-[#F2F5F0]">
                  Grounded Finding Inspector
                </h3>
              </div>

              {/* WHAT WE FOUND */}
              <div className="space-y-1">
                <span className="text-xs font-sans font-semibold uppercase tracking-wider text-[#C5F5D5]">
                  WHAT WE FOUND
                </span>
                <p className="text-sm text-[#F2F5F0] font-sans leading-relaxed">
                  {inspectorFinding.explanation}
                </p>
              </div>

              {/* WHY IT MATTERS */}
              <div className="space-y-1">
                <span className="text-xs font-sans font-semibold uppercase tracking-wider text-[#8A9B91]">
                  WHY IT MATTERS
                </span>
                <p className="text-xs text-[#8A9B91] font-sans leading-relaxed">
                  {inspectorFinding.applicable_policy_rule?.rule ||
                    inspectorFinding.policy_requirement ||
                    'Governed by internal corporate risk guidelines.'}
                </p>
              </div>

              {/* RECOMMENDED ACTION */}
              {inspectorFinding.recommended_action && (
                <div className="p-3.5 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.1)] space-y-1">
                  <span className="text-xs font-sans font-semibold uppercase tracking-wider text-[#A8E6BF]">
                    RECOMMENDED ACTION
                  </span>
                  <p className="text-xs text-[#F2F5F0] font-sans leading-relaxed">
                    {inspectorFinding.recommended_action}
                  </p>
                </div>
              )}

              {/* EVIDENCE CITATION DETAILS */}
              <div className="space-y-2 pt-2 border-t border-[rgba(197,245,213,0.08)]">
                <span className="text-xs font-sans font-semibold uppercase tracking-wider text-[#C5F5D5] flex items-center gap-1.5">
                  <IconCheckCircle className="w-3.5 h-3.5 text-[#C5F5D5]" />
                  <span>EVIDENCE</span>
                </span>

                {inspectorFinding.evidence_quote ? (
                  <div className="p-3 rounded-lg bg-[#080B0A] font-editorial italic text-xs text-[#C5F5D5] leading-relaxed line-clamp-3 border border-[rgba(197,245,213,0.08)]">
                    "{inspectorFinding.evidence_quote}"
                  </div>
                ) : inspectorFinding.potential_omission ? (
                  <div className="text-xs text-[#F87171] p-2.5 bg-[#180E10] rounded-lg border border-[#F87171]/20 font-sans">
                    Clause terms omitted in current document text.
                  </div>
                ) : null}

                <div className="grid grid-cols-2 gap-2 text-xs font-mono pt-1">
                  <div className="text-[#8A9B91]">
                    Clause:{' '}
                    <span className="text-[#F2F5F0]">
                      {inspectorFinding.clause_id || 'Omission'}
                    </span>
                  </div>
                  <div className="text-[#8A9B91]">
                    Page:{' '}
                    <span className="text-[#F2F5F0]">
                      {inspectorFinding.page_number || 'N/A'}
                    </span>
                  </div>
                  <div className="text-[#8A9B91]">
                    Policy Rule:{' '}
                    <span className="text-[#A8E6BF]">{inspectorFinding.policy_id}</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-20 text-[#8A9B91] text-sm font-sans space-y-2">
              <IconGraph className="w-8 h-8 mx-auto text-[#C5F5D5] opacity-40" />
              <div>Click any node on the graph to inspect evidence and policy details.</div>
            </div>
          )}

          {/* OPEN IN EVIDENCE EXPLORER BUTTON */}
          {inspectorFinding && onNavigateToFinding && (
            <button
              onClick={() => onNavigateToFinding(inspectorFinding)}
              className="w-full py-3 rounded-xl bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] text-xs font-sans font-bold flex items-center justify-center gap-2 transition-all shadow-md shadow-[#C5F5D5]/10 mt-4"
            >
              <span>OPEN IN EVIDENCE EXPLORER</span>
              <IconArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* 3. FOCUSED 4-STAGE ACCESSIBLE CARDS (Visible in Focused Mode) */}
      {viewMode === 'focused' && currentFinding && (
        <div className="pt-4 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-editorial text-2xl font-light text-[#F2F5F0]">
              Cause & Effect Sequence
            </h3>
            <span className="text-xs font-mono text-[#8A9B91]">
              Finding #{selectedFindingIndex + 1} of {findings.length}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Card 1: Contract Clause */}
            <div className="p-5 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] space-y-2.5">
              <div className="flex items-center justify-between text-xs font-mono text-[#8A9B91]">
                <span className="text-[#C5F5D5] font-semibold">1. CONTRACT CLAUSE</span>
                <span>{currentFinding.page_number ? `Page ${currentFinding.page_number}` : 'Omission'}</span>
              </div>
              <h4 className="font-sans font-semibold text-sm text-[#F2F5F0]">
                {currentFinding.clause_id ? `Clause ${currentFinding.clause_id}` : 'Omitted Clause'}
              </h4>
              <p className="font-editorial italic text-xs text-[#C5F5D5] leading-relaxed line-clamp-4 bg-[#080B0A] p-3 rounded-xl border border-white/5">
                "{currentFinding.evidence_quote || 'No clause text provided in contract (potential omission).'}"
              </p>
            </div>

            {/* Card 2: Company Policy */}
            <div className="p-5 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] space-y-2.5">
              <div className="flex items-center justify-between text-xs font-mono text-[#8A9B91]">
                <span className="text-[#A8E6BF] font-semibold">2. COMPANY POLICY</span>
                <span>{currentFinding.policy_id}</span>
              </div>
              <h4 className="font-sans font-semibold text-sm text-[#F2F5F0]">
                {CLAUSE_CATEGORIES[currentFinding.clause_category] || currentFinding.clause_category} Standard
              </h4>
              <p className="text-xs text-[#8A9B91] font-sans leading-relaxed line-clamp-4 bg-[#080B0A] p-3 rounded-xl border border-white/5">
                {currentFinding.applicable_policy_rule?.rule ||
                  currentFinding.policy_requirement ||
                  'Evaluation criteria defined in company playbook.'}
              </p>
            </div>

            {/* Card 3: Identified Risk */}
            <div className="p-5 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] space-y-2.5">
              <div className="flex items-center justify-between text-xs font-mono text-[#8A9B91]">
                <span
                  className="font-semibold"
                  style={{
                    color: (RISK_LEVELS[currentFinding.risk_level] || RISK_LEVELS.medium).color,
                  }}
                >
                  3. IDENTIFIED RISK
                </span>
                <span
                  className="px-2 py-0.5 rounded text-[10px] font-sans font-semibold"
                  style={{
                    color: (RISK_LEVELS[currentFinding.risk_level] || RISK_LEVELS.medium).color,
                    backgroundColor: `${(RISK_LEVELS[currentFinding.risk_level] || RISK_LEVELS.medium).color}15`,
                  }}
                >
                  {(RISK_LEVELS[currentFinding.risk_level] || RISK_LEVELS.medium).label}
                </span>
              </div>
              <h4 className="font-sans font-semibold text-sm text-[#F2F5F0]">
                Policy Deviation Detected
              </h4>
              <p className="text-xs text-[#F2F5F0]/90 font-sans leading-relaxed line-clamp-4 bg-[#080B0A] p-3 rounded-xl border border-white/5">
                {currentFinding.explanation}
              </p>
            </div>

            {/* Card 4: Recommended Action */}
            <div className="p-5 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] space-y-2.5">
              <div className="flex items-center justify-between text-xs font-mono text-[#8A9B91]">
                <span className="text-[#C5F5D5] font-semibold">4. RECOMMENDED ACTION</span>
                <span className="text-[#A8E6BF] font-mono text-[10px]">REMEDIATION</span>
              </div>
              <h4 className="font-sans font-semibold text-sm text-[#F2F5F0]">
                Suggested Redline
              </h4>
              <p className="text-xs text-[#C5F5D5] font-sans leading-relaxed line-clamp-4 bg-[#080B0A] p-3 rounded-xl border border-white/5">
                {currentFinding.recommended_action || 'Consult qualified legal counsel to formulate remediation.'}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
