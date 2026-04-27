'use client'

import { useState, useEffect } from 'react'

interface WBSItem {
  id: string
  code: string
  name: string
  description: string | null
  planned_value: number
  actual_cost: number
  earned_value: number
  percent_complete: number
  status: string
}

interface EVAMetrics {
  total_pv: number
  total_ev: number
  total_ac: number
  spi: number
  cpi: number
  sv: number
  cv: number
  bac: number
  eac: number
  status: string
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8006'

export default function ProjectPage() {
  const [wbs, setWbs] = useState<WBSItem[]>([])
  const [eva, setEva] = useState<EVAMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [wbsRes, evaRes] = await Promise.allSettled([
          fetch(`${API_BASE}/project/wbs`),
          fetch(`${API_BASE}/project/eva`),
        ])

        if (wbsRes.status === 'fulfilled' && wbsRes.value.ok) {
          setWbs(await wbsRes.value.json())
        }
        if (evaRes.status === 'fulfilled' && evaRes.value.ok) {
          setEva(await evaRes.value.json())
        }
      } catch (err) {
        setError('Unable to connect to Project Management service')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  // Fallback values when API not available
  const evaDisplay = eva || {
    total_pv: 100000, total_ev: 0, total_ac: 0,
    spi: 0, cpi: 0, sv: 0, cv: 0, bac: 100000, eac: 100000, status: 'not_started'
  }

  const wbsDisplay = wbs.length > 0 ? wbs : [
    { id: '1', code: '1.0', name: 'Messaging Engine', planned_value: 20000, actual_cost: 0, earned_value: 0, percent_complete: 0, status: 'not_started', description: null },
    { id: '2', code: '2.0', name: 'EDA Pipeline', planned_value: 15000, actual_cost: 0, earned_value: 0, percent_complete: 0, status: 'not_started', description: null },
    { id: '3', code: '3.0', name: 'DSL Engine', planned_value: 15000, actual_cost: 0, earned_value: 0, percent_complete: 0, status: 'not_started', description: null },
    { id: '4', code: '4.0', name: 'Security Layer', planned_value: 10000, actual_cost: 0, earned_value: 0, percent_complete: 0, status: 'not_started', description: null },
    { id: '5', code: '5.0', name: 'Dashboard', planned_value: 20000, actual_cost: 0, earned_value: 0, percent_complete: 0, status: 'not_started', description: null },
    { id: '6', code: '6.0', name: 'Monitoring', planned_value: 10000, actual_cost: 0, earned_value: 0, percent_complete: 0, status: 'not_started', description: null },
    { id: '7', code: '7.0', name: 'Edge/Fog Simulation', planned_value: 10000, actual_cost: 0, earned_value: 0, percent_complete: 0, status: 'not_started', description: null },
  ]

  const formatCurrency = (v: number) => `$${v.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`

  const statusColor = (status: string) => {
    switch (status) {
      case 'on_track': return 'text-green-400'
      case 'at_risk': return 'text-yellow-400'
      case 'behind': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const taskStatusLabel = (status: string) => {
    switch (status) {
      case 'completed': return { text: 'Complete', cls: 'bg-green-500/20 text-green-400' }
      case 'in_progress': return { text: 'In Progress', cls: 'bg-command-500/20 text-command-400' }
      case 'blocked': return { text: 'Blocked', cls: 'bg-red-500/20 text-red-400' }
      default: return { text: 'Not Started', cls: 'bg-gray-500/20 text-gray-400' }
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">
          WBS & Earned Value Analysis
        </h1>
        <p className="text-gray-400 mt-1">
          Project tracking and delivery metrics
          {error && <span className="text-yellow-500/60 text-xs ml-3">({error})</span>}
        </p>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading project data...</div>
      ) : (
        <>
          {/* EVA Summary Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {[
              { label: 'Planned Value (PV)', value: formatCurrency(evaDisplay.total_pv), color: 'text-gray-300' },
              { label: 'Earned Value (EV)', value: formatCurrency(evaDisplay.total_ev), color: 'text-command-400' },
              { label: 'Schedule Performance (SPI)', value: evaDisplay.spi.toFixed(2), color: evaDisplay.spi >= 0.9 ? 'text-green-400' : evaDisplay.spi >= 0.7 ? 'text-yellow-400' : 'text-red-400', desc: evaDisplay.spi >= 1.0 ? 'Ahead of schedule' : evaDisplay.spi >= 0.9 ? 'Slightly behind schedule' : 'Behind schedule' },
              { label: 'Cost Performance (CPI)', value: evaDisplay.cpi.toFixed(2), color: evaDisplay.cpi >= 1.0 ? 'text-green-400' : evaDisplay.cpi >= 0.9 ? 'text-yellow-400' : 'text-red-400', desc: evaDisplay.cpi >= 1.0 ? 'Under budget' : 'Over budget' },
            ].map(m => (
              <div key={m.label} className="glass-card p-6 border-t-4 border-t-gray-800 hover:border-t-command-500 transition-colors">
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">{m.label}</h3>
                <div className={`text-2xl font-bold ${m.color}`}>{m.value}</div>
                {m.desc && <p className="text-xs text-gray-500 mt-2">{m.desc}</p>}
              </div>
            ))}
          </div>

          {/* Additional EVA Metrics */}
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
            {[
              { label: 'Actual Cost (AC)', value: formatCurrency(evaDisplay.total_ac) },
              { label: 'Schedule Variance (SV)', value: formatCurrency(evaDisplay.sv), color: evaDisplay.sv >= 0 ? 'text-green-400' : 'text-red-400' },
              { label: 'Cost Variance (CV)', value: formatCurrency(evaDisplay.cv), color: evaDisplay.cv >= 0 ? 'text-green-400' : 'text-red-400' },
              { label: 'Budget at Complete (BAC)', value: formatCurrency(evaDisplay.bac) },
              { label: 'Estimate at Complete (EAC)', value: formatCurrency(evaDisplay.eac) },
            ].map(m => (
              <div key={m.label} className="glass-card p-4">
                <h4 className="text-xs text-gray-500 mb-1">{m.label}</h4>
                <div className={`text-lg font-bold ${m.color || 'text-white'}`}>{m.value}</div>
              </div>
            ))}
          </div>

          {/* WBS Table */}
          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Work Breakdown Structure (WBS)</h2>
            <div className="space-y-4">
              {wbsDisplay.map(task => {
                const st = taskStatusLabel(task.status)
                return (
                  <div key={task.id} className="flex items-center gap-4 group">
                    <div className="w-12 text-xs font-mono text-gray-500">{task.code}</div>
                    <div className={`flex-1 text-sm ${task.code.endsWith('.0') ? 'font-semibold text-white' : 'text-gray-400 pl-4'}`}>
                      {task.name}
                    </div>
                    <div className="w-24 text-xs text-right text-gray-500 font-mono">
                      {formatCurrency(task.planned_value)}
                    </div>
                    <div className="w-48 flex items-center gap-3">
                      <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full transition-all duration-500 ${task.percent_complete >= 100 ? 'bg-green-500' : task.percent_complete > 0 ? 'bg-command-500' : 'bg-gray-700'}`} 
                          style={{ width: `${Math.min(task.percent_complete, 100)}%` }}
                        ></div>
                      </div>
                      <div className="w-12 text-xs text-right text-gray-500">{task.percent_complete}%</div>
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${st.cls}`}>{st.text}</span>
                  </div>
                )
              })}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
