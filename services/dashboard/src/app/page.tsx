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
  id: string
  type: string
  severity: string
  zone: string
  time: string
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<MetricCard[]>([
    { label: 'Active Incidents', value: 3, change: '+1', color: 'text-red-400', icon: '🔥' },
    { label: 'Messages Sent', value: 1247, change: '+23', color: 'text-command-400', icon: '📨' },
    { label: 'Protocols Executed', value: 42, change: '+5', color: 'text-green-400', icon: '📜' },
    { label: 'Avg Latency', value: '47ms', color: 'text-yellow-400', icon: '⚡' },
    { label: 'Active Responders', value: 18, change: '+2', color: 'text-purple-400', icon: '👥' },
    { label: 'System Health', value: '99.9%', color: 'text-green-400', icon: '💚' },
  ])

  const [incidents, setIncidents] = useState<Incident[]>([
    { id: '1', type: 'fire_alert', severity: 'critical', zone: 'zone-alpha', time: '2 min ago' },
    { id: '2', type: 'medical_emergency', severity: 'high', zone: 'zone-beta', time: '5 min ago' },
    { id: '3', type: 'intrusion_detected', severity: 'medium', zone: 'zone-alpha', time: '12 min ago' },
    { id: '4', type: 'network_failure', severity: 'low', zone: 'zone-beta', time: '25 min ago' },
  ])

  const [heatmapData] = useState([
    [0, 1, 0, 2, 1, 0, 3, 1],
    [1, 0, 2, 1, 0, 4, 2, 0],
    [0, 2, 1, 3, 2, 1, 0, 1],
    [2, 0, 0, 1, 4, 2, 1, 0],
  ])

  const zones = ['Zone A1', 'Zone A2', 'Zone A3', 'Zone A4', 'Zone B1', 'Zone B2', 'Zone B3', 'Zone B4']
  const timeSlots = ['00:00', '06:00', '12:00', '18:00']

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
            {new Date().toLocaleString()}
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
          <div className="space-y-3">
            {incidents.map((incident) => (
              <div
                key={incident.id}
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
                      {eventTypeLabel(incident.type)}
                    </p>
                    <p className="text-xs text-gray-500">{incident.zone} · {incident.time}</p>
                  </div>
                </div>
                <span className={`status-badge ${severityClass(incident.severity)}`}>
                  {incident.severity}
                </span>
              </div>
            ))}
          </div>
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
            {[
              { name: 'Gateway', status: 'healthy', latency: '12ms' },
              { name: 'Auth Service', status: 'healthy', latency: '8ms' },
              { name: 'Messaging', status: 'healthy', latency: '15ms' },
              { name: 'Events Pipeline', status: 'healthy', latency: '23ms' },
              { name: 'Prediction', status: 'healthy', latency: '45ms' },
              { name: 'DSL Engine', status: 'healthy', latency: '11ms' },
              { name: 'Redpanda', status: 'healthy', latency: '3ms' },
              { name: 'PostgreSQL', status: 'healthy', latency: '5ms' },
              { name: 'Redis', status: 'healthy', latency: '1ms' },
            ].map((service, i) => (
              <div key={i} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${
                    service.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
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
