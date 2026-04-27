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
  location: string
  created_at: string
}

interface ServiceHealth {
  name: string
  status: 'healthy' | 'unhealthy' | 'unknown'
  latency: string
}

const GATEWAY_URL = process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://localhost:8000'
const EVENTS_URL = process.env.NEXT_PUBLIC_EVENTS_URL || 'http://localhost:8003'

export default function Dashboard() {
  const [metrics, setMetrics] = useState<MetricCard[]>([
    { label: 'Active Incidents', value: '...', color: 'text-red-400', icon: '🔥' },
    { label: 'Messages Sent', value: '...', color: 'text-command-400', icon: '📨' },
    { label: 'Protocols Executed', value: '...', color: 'text-green-400', icon: '📜' },
    { label: 'Avg Latency', value: '...', color: 'text-yellow-400', icon: '⚡' },
    { label: 'Active Responders', value: '...', color: 'text-purple-400', icon: '👥' },
    { label: 'System Health', value: '...', color: 'text-green-400', icon: '💚' },
  ])

  const [incidents, setIncidents] = useState<Incident[]>([])
  const [services, setServices] = useState<ServiceHealth[]>([])
  const [loadingIncidents, setLoadingIncidents] = useState(true)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const [heatmapData] = useState([
    [0, 1, 0, 2, 1, 0, 3, 1],
    [1, 0, 2, 1, 0, 4, 2, 0],
    [0, 2, 1, 3, 2, 1, 0, 1],
    [2, 0, 0, 1, 4, 2, 1, 0],
  ])

  const zones = ['Zone A1', 'Zone A2', 'Zone A3', 'Zone A4', 'Zone B1', 'Zone B2', 'Zone B3', 'Zone B4']
  const timeSlots = ['00:00', '06:00', '12:00', '18:00']

  // Fetch gateway health status
  useEffect(() => {
    const fetchHealth = async () => {
      const serviceList: ServiceHealth[] = [
        { name: 'Gateway', status: 'unknown', latency: '-' },
        { name: 'Auth Service', status: 'unknown', latency: '-' },
        { name: 'Messaging', status: 'unknown', latency: '-' },
        { name: 'Events Pipeline', status: 'unknown', latency: '-' },
        { name: 'Prediction', status: 'unknown', latency: '-' },
        { name: 'DSL Engine', status: 'unknown', latency: '-' },
        { name: 'Redpanda', status: 'unknown', latency: '-' },
        { name: 'PostgreSQL', status: 'unknown', latency: '-' },
        { name: 'Redis', status: 'unknown', latency: '-' },
      ]

      try {
        const start = performance.now()
        const res = await fetch(`${GATEWAY_URL}/health`)
        const elapsed = Math.round(performance.now() - start)

        if (res.ok) {
          const data = await res.json()

          // Update gateway status
          serviceList[0] = { name: 'Gateway', status: 'healthy', latency: `${elapsed}ms` }

          // Update downstream services if health endpoint returns them
          if (data.services) {
            const svcMap: Record<string, number> = {
              'auth': 1, 'messaging': 2, 'events': 3,
              'prediction': 4, 'dsl_engine': 5, 'dsl-engine': 5
            }
            for (const [svcName, svcData] of Object.entries(data.services || {})) {
              const idx = svcMap[svcName]
              if (idx !== undefined) {
                const sd = svcData as any
                serviceList[idx] = {
                  name: serviceList[idx].name,
                  status: sd.healthy ? 'healthy' : 'unhealthy',
                  latency: sd.latency_ms ? `${sd.latency_ms}ms` : '-',
                }
              }
            }
          }

          // Count healthy services
          const healthyCount = serviceList.filter(s => s.status === 'healthy').length
          const totalCount = serviceList.length
          const healthPct = Math.round((healthyCount / totalCount) * 100)

          setMetrics(prev => prev.map(m => {
            if (m.label === 'System Health') return { ...m, value: `${healthPct}%` }
            if (m.label === 'Avg Latency') return { ...m, value: `${elapsed}ms` }
            return m
          }))
        }
      } catch {
        serviceList[0] = { name: 'Gateway', status: 'unhealthy', latency: '-' }
      }

      setServices(serviceList)
    }

    fetchHealth()
    const interval = setInterval(fetchHealth, 15000)
    return () => clearInterval(interval)
  }, [])

  // Fetch live incidents from Events service + stats
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [incRes, statsRes] = await Promise.allSettled([
          fetch(`${EVENTS_URL}/events/history?limit=10`),
          fetch(`${EVENTS_URL}/events/stats`),
        ])

        if (incRes.status === 'fulfilled' && incRes.value.ok) {
          const data = await incRes.value.json()
          setIncidents(data.slice(0, 5))
          setMetrics(prev => prev.map(m => 
            m.label === 'Active Incidents' ? { ...m, value: data.length } : m
          ))
        }

        if (statsRes.status === 'fulfilled' && statsRes.value.ok) {
          const stats = await statsRes.value.json()
          setMetrics(prev => prev.map(m => {
            if (m.label === 'Messages Sent') return { ...m, value: stats.total_events || 0 }
            return m
          }))
        }
      } catch {
        // Use fallback data
        setIncidents([
          { event_id: 'demo-1', event_type: 'fire_alert', severity: 'critical', zone: 'zone-alpha', location: 'zone-alpha-temp', created_at: new Date().toISOString() },
          { event_id: 'demo-2', event_type: 'medical_emergency', severity: 'high', zone: 'zone-beta', location: 'zone-beta-smoke', created_at: new Date().toISOString() },
          { event_id: 'demo-3', event_type: 'intrusion_detected', severity: 'medium', zone: 'zone-alpha', location: 'zone-alpha-motion', created_at: new Date().toISOString() },
        ])
      } finally {
        setLoadingIncidents(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [])

  const severityClass = (severity: string) => {
    switch (severity) {
      case 'critical': return 'severity-critical'
      case 'high': return 'severity-high'
      case 'medium': return 'severity-medium'
      case 'low': return 'severity-low'
      default: return 'severity-low'
    }
  }

  const eventTypeLabel = (type: string) => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
  }

  const timeAgo = (iso: string) => {
    try {
      const diff = Date.now() - new Date(iso).getTime()
      const mins = Math.floor(diff / 60000)
      if (mins < 1) return 'just now'
      if (mins < 60) return `${mins} min ago`
      return `${Math.floor(mins / 60)}h ago`
    } catch {
      return ''
    }
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-command-400 to-command-600 bg-clip-text text-transparent">
            Command Center
          </h1>
          <p className="text-gray-400 mt-1">Real-time emergency monitoring and response</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-4 py-2 glass-card">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span className="text-sm text-gray-300">Live</span>
          </div>
          <div className="px-4 py-2 glass-card text-sm text-gray-400">
            {mounted ? new Date().toLocaleString() : 'Loading status...'}
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {metrics.map((metric, i) => (
          <div key={i} className="metric-card hover:border-command-500/30 transition-all duration-300 group">
            <div className="flex items-center justify-between">
              <span className="text-2xl group-hover:scale-110 transition-transform">{metric.icon}</span>
              {metric.change && (
                <span className={`text-xs ${metric.change.startsWith('+') ? 'text-green-400' : 'text-red-400'}`}>
                  {metric.change}
                </span>
              )}
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
            🗺️ Incident Heatmap
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
                    title={`${zones[ci]} at ${timeSlots[ri]}: ${val} incidents`}
                  >
                    {val > 0 && <span className="text-gray-300">{val}</span>}
                  </div>
                ))}
              </div>
            ))}
          </div>
          <div className="flex items-center gap-4 mt-4 text-xs text-gray-500">
            <span className="flex items-center gap-1"><div className="w-3 h-3 rounded heat-0 border border-gray-700"></div> None</span>
            <span className="flex items-center gap-1"><div className="w-3 h-3 rounded heat-1 border border-gray-700"></div> Low</span>
            <span className="flex items-center gap-1"><div className="w-3 h-3 rounded heat-2 border border-gray-700"></div> Medium</span>
            <span className="flex items-center gap-1"><div className="w-3 h-3 rounded heat-3 border border-gray-700"></div> High</span>
            <span className="flex items-center gap-1"><div className="w-3 h-3 rounded heat-4 border border-gray-700"></div> Critical</span>
          </div>
        </div>

        {/* Active Incidents */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            🚨 Active Incidents
          </h2>
          {loadingIncidents ? (
            <div className="text-center py-8 text-gray-500 text-sm">Loading live incidents...</div>
          ) : (
            <div className="space-y-3">
              {incidents.map((incident) => (
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
                      <p className="text-sm font-medium text-white group-hover:text-command-400 transition-colors">
                        {eventTypeLabel(incident.event_type)}
                      </p>
                      <p className="text-xs text-gray-500">{incident.zone} · {mounted ? timeAgo(incident.created_at) : '...'}</p>
                    </div>
                  </div>
                  <span className={`status-badge ${severityClass(incident.severity)}`}>
                    {incident.severity}
                  </span>
                </div>
              ))}
              {incidents.length === 0 && (
                <div className="text-center py-6 text-gray-500 text-sm">No active incidents</div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Protocol Execution Log + System Health */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 glass-card p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            📜 Recent Protocol Executions
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-gray-500 border-b border-gray-700/50">
                  <th className="text-left py-3 px-4">Protocol</th>
                  <th className="text-left py-3 px-4">Trigger</th>
                  <th className="text-left py-3 px-4">Actions</th>
                  <th className="text-left py-3 px-4">Latency</th>
                  <th className="text-left py-3 px-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700/30">
                <tr className="hover:bg-gray-800/30">
                  <td className="py-3 px-4 text-command-400">Fire Response Alpha</td>
                  <td className="py-3 px-4">fire_alert</td>
                  <td className="py-3 px-4">4 actions</td>
                  <td className="py-3 px-4 text-green-400">23ms</td>
                  <td className="py-3 px-4"><span className="status-badge bg-green-500/20 text-green-400">completed</span></td>
                </tr>
                <tr className="hover:bg-gray-800/30">
                  <td className="py-3 px-4 text-command-400">Medical Dispatch</td>
                  <td className="py-3 px-4">medical_emergency</td>
                  <td className="py-3 px-4">3 actions</td>
                  <td className="py-3 px-4 text-green-400">18ms</td>
                  <td className="py-3 px-4"><span className="status-badge bg-green-500/20 text-green-400">completed</span></td>
                </tr>
                <tr className="hover:bg-gray-800/30">
                  <td className="py-3 px-4 text-command-400">Zone Lockdown</td>
                  <td className="py-3 px-4">intrusion_detected</td>
                  <td className="py-3 px-4">5 actions</td>
                  <td className="py-3 px-4 text-yellow-400">156ms</td>
                  <td className="py-3 px-4"><span className="status-badge bg-yellow-500/20 text-yellow-400">running</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            💚 System Health
          </h2>
          <div className="space-y-4">
            {(services.length > 0 ? services : [
              { name: 'Gateway', status: 'unknown' as const, latency: '-' },
              { name: 'Auth Service', status: 'unknown' as const, latency: '-' },
              { name: 'Messaging', status: 'unknown' as const, latency: '-' },
              { name: 'Events Pipeline', status: 'unknown' as const, latency: '-' },
              { name: 'Prediction', status: 'unknown' as const, latency: '-' },
              { name: 'DSL Engine', status: 'unknown' as const, latency: '-' },
              { name: 'Redpanda', status: 'unknown' as const, latency: '-' },
              { name: 'PostgreSQL', status: 'unknown' as const, latency: '-' },
              { name: 'Redis', status: 'unknown' as const, latency: '-' },
            ]).map((service, i) => (
              <div key={i} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${
                    service.status === 'healthy' ? 'bg-green-500' : 
                    service.status === 'unhealthy' ? 'bg-red-500' : 'bg-gray-600'
                  }`}></div>
                  <span className="text-sm text-gray-300">{service.name}</span>
                </div>
                <span className="text-xs text-gray-500">{service.latency}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
