'use client'

import { useState, useEffect } from 'react'

interface MetricCard {
  label: string
  value: string | number
  change?: string
  color: string
  icon: string
}

interface Incident {
  event_id: string
  event_type: string
  severity: string
  zone: string
  created_at: string
}

interface ProtocolExecution {
  id: string
  protocol_name?: string
  status: string
  execution_time_ms: number
  completed_at: string
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<MetricCard[]>([
    { label: 'Active Incidents', value: '...', color: 'text-red-400', icon: '🔥' },
    { label: 'Total Events', value: '...', color: 'text-command-400', icon: '📨' },
    { label: 'Protocols Active', value: '...', color: 'text-green-400', icon: '📜' },
    { label: 'Avg Latency', value: '14ms', color: 'text-yellow-400', icon: '⚡' },
    { label: 'Edge Nodes', value: 2, color: 'text-purple-400', icon: '👥' },
    { label: 'System Health', value: '99.9%', color: 'text-green-400', icon: '💚' },
  ])

  const [incidents, setIncidents] = useState<Incident[]>([])
  const [executions, setExecutions] = useState<ProtocolExecution[]>([])
  const [health, setHealth] = useState<any[]>([])
  const [heatmapData, setHeatmapData] = useState<number[][]>(Array(4).fill(0).map(() => Array(8).fill(0)))

  useEffect(() => {
    const fetchData = async () => {
      try {
        // 1. Fetch Incidents & Update Heatmap
        const incRes = await fetch('http://localhost:8003/events/history?limit=5')
        if (incRes.ok) {
          const data = await incRes.json()
          setIncidents(data)
          
          const newHeatmap = Array(4).fill(0).map(() => Array(8).fill(0))
          data.forEach((inc: any, i: number) => {
            const row = i % 4
            const col = (i * 2) % 8
            newHeatmap[row][col] = (newHeatmap[row][col] + 1) % 5
          })
          setHeatmapData(newHeatmap)
        }

        // 2. Fetch Stats for Metrics
        const statsRes = await fetch('http://localhost:8003/events/stats')
        if (statsRes.ok) {
          const stats = await statsRes.json()
          
          // 3. Fetch Protocol Count
          const protoRes = await fetch('http://localhost:8005/protocols')
          const protos = await protoRes.json()

          setMetrics(prev => prev.map(m => {
            if (m.label === 'Active Incidents') return { ...m, value: stats.total_events - (stats.by_severity?.low || 0) }
            if (m.label === 'Total Events') return { ...m, value: stats.total_events }
            if (m.label === 'Protocols Active') return { ...m, value: Array.isArray(protos) ? protos.length : 0 }
            return m
          }))
        }

        // 4. Update System Health (Simulated ping to Gateway)
        const services = ['Gateway', 'Auth', 'Messaging', 'Events', 'Prediction', 'DSL Engine', 'Redpanda', 'PostgreSQL']
        setHealth(services.map(s => ({
          name: s,
          status: 'healthy',
          latency: `${Math.floor(Math.random() * 20) + 5}ms`
        })))

      } catch (err) {
        console.error("Dashboard fetch error:", err)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [])

  const zones = ['Zone A1', 'Zone A2', 'Zone A3', 'Zone A4', 'Zone B1', 'Zone B2', 'Zone B3', 'Zone B4']
  const timeSlots = ['00:00', '06:00', '12:00', '18:00']

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-command-400 to-command-600 bg-clip-text text-transparent">
            Command Center
          </h1>
          <p className="text-gray-400 mt-1">Live Edge/Fog Emergency Infrastructure Overview</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-4 py-2 glass-card">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span className="text-sm text-gray-300">Live Backend Stream</span>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {metrics.map((metric, i) => (
          <div key={i} className="metric-card hover:border-command-500/30 transition-all duration-300 group">
            <div className="flex items-center justify-between">
              <span className="text-2xl group-hover:scale-110 transition-transform">{metric.icon}</span>
            </div>
            <span className={`metric-value ${metric.color}`}>{metric.value}</span>
            <span className="metric-label">{metric.label}</span>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Incident Heatmap */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            🗺️ Dynamic Incident Heatmap
          </h2>
          <div className="space-y-2">
            <div className="grid grid-cols-9 gap-1 text-xs text-gray-500">
              <div></div>
              {zones.map((z, i) => (
                <div key={i} className="text-center truncate">{z}</div>
              ))}
            </div>
            {heatmapData.map((row, ri) => (
              <div key={ri} className="grid grid-cols-9 gap-1">
                <div className="text-xs text-gray-500 flex items-center">{timeSlots[ri]}</div>
                {row.map((val, ci) => (
                  <div
                    key={ci}
                    className={`h-10 rounded-md heat-${val} border border-gray-700/30 flex items-center justify-center text-xs transition-all hover:scale-105 cursor-pointer`}
                  >
                    {val > 0 && <span className="text-gray-300">{val}</span>}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>

        {/* Active Incidents */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            🚨 Real-Time Stream
          </h2>
          <div className="space-y-3">
            {incidents.length > 0 ? incidents.map((incident) => (
              <div
                key={incident.event_id}
                className="flex items-center justify-between p-4 rounded-lg bg-gray-800/50 border border-gray-700/30 hover:border-gray-600/50 transition-all cursor-pointer group"
              >
                <div className="flex items-center gap-4">
                  <div className={`w-3 h-3 rounded-full ${
                    incident.severity === 'critical' ? 'bg-red-500 animate-pulse' :
                    incident.severity === 'high' ? 'bg-orange-500' :
                    incident.severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                  }`}></div>
                  <div>
                    <p className="text-sm font-medium text-white group-hover:text-command-400 transition-colors uppercase">
                      {incident.event_type.replace('_', ' ')}
                    </p>
                    <p className="text-xs text-gray-500">{incident.zone} · {new Date(incident.created_at).toLocaleTimeString()}</p>
                  </div>
                </div>
                <span className={`status-badge text-xs px-2 py-0.5 rounded-full ${
                  incident.severity === 'critical' ? 'bg-red-500/20 text-red-400' :
                  incident.severity === 'high' ? 'bg-orange-500/20 text-orange-400' :
                  incident.severity === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                  'bg-blue-500/20 text-blue-400'
                }`}>
                  {incident.severity}
                </span>
              </div>
            )) : (
              <div className="text-center py-10 text-gray-600 italic text-sm">Waiting for edge node data...</div>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 glass-card p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            📜 Recent System Logs
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-gray-500 border-b border-gray-700/50">
                  <th className="text-left py-3 px-4">Event</th>
                  <th className="text-left py-3 px-4">Source</th>
                  <th className="text-left py-3 px-4">Zone</th>
                  <th className="text-left py-3 px-4">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700/30">
                {incidents.map((inc) => (
                  <tr key={inc.event_id} className="hover:bg-gray-800/30">
                    <td className="py-3 px-4 text-command-400 uppercase font-mono text-xs">{inc.event_type}</td>
                    <td className="py-3 px-4 text-gray-300">edge-node</td>
                    <td className="py-3 px-4 text-gray-400">{inc.zone}</td>
                    <td className="py-3 px-4 text-gray-500">{new Date(inc.created_at).toLocaleTimeString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            💚 System Health
          </h2>
          <div className="space-y-4">
            {health.map((service, i) => (
              <div key={i} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full bg-green-500`}></div>
                  <span className="text-sm text-gray-300">{service.name}</span>
                </div>
                <span className="text-xs text-gray-500 font-mono">{service.latency}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
