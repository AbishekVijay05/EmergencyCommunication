'use client'

import { useState, useEffect } from 'react'

export default function AnalyticsPage() {
  const [stats, setStats] = useState<any>(null)
  
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch('http://localhost:8003/events/stats')
        if (res.ok) {
          const data = await res.json()
          setStats(data)
        }
      } catch (err) {
        console.error(err)
      }
    }
    fetchStats()
    const interval = setInterval(fetchStats, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-teal-400 to-emerald-500 bg-clip-text text-transparent">
          Live System Analytics
        </h1>
        <p className="text-gray-400 mt-1">Real-time metrics streaming from Postgres and Redpanda (Kafka)</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="glass-card p-6">
          <h3 className="text-sm font-medium text-gray-400 mb-1">Total Events Processed</h3>
          <div className="text-3xl font-bold text-white mb-4">
            {stats ? stats.total_events.toLocaleString() : '...'}
          </div>
          {/* Faux Chart */}
          <div className="flex items-end gap-1 h-16">
            {[40, 45, 35, 50, 42, 48, 38, 42].map((v, i) => (
              <div key={i} className="flex-1 bg-teal-500/20 rounded-t border-t border-teal-500/50 hover:bg-teal-500/40 transition-colors" style={{ height: `${v}%` }}></div>
            ))}
          </div>
        </div>

        <div className="glass-card p-6">
          <h3 className="text-sm font-medium text-gray-400 mb-1">Fire Alerts</h3>
          <div className="text-3xl font-bold text-white mb-4">
            {stats?.by_type?.fire_alert || 0}
          </div>
          {/* Faux Chart */}
          <div className="flex items-end gap-1 h-16">
            {[20, 30, 40, 60, 50, 80, 70, 95].map((v, i) => (
              <div key={i} className="flex-1 bg-orange-500/20 rounded-t border-t border-orange-500/50 hover:bg-orange-500/40 transition-colors" style={{ height: `${v}%` }}></div>
            ))}
          </div>
        </div>

        <div className="glass-card p-6">
          <h3 className="text-sm font-medium text-gray-400 mb-1">Intrusion Detections</h3>
          <div className="text-3xl font-bold text-white mb-4">
            {stats?.by_type?.intrusion_detected || 0}
          </div>
          {/* Faux Chart */}
          <div className="flex items-end gap-1 h-16">
            {[10, 8, 9, 8, 7, 8, 9, 8].map((v, i) => (
              <div key={i} className="flex-1 bg-purple-500/20 rounded-t border-t border-purple-500/50 hover:bg-purple-500/40 transition-colors" style={{ height: `${v*4}%` }}></div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Severity Breakdown</h2>
          <div className="space-y-4">
            {['critical', 'high', 'medium', 'low'].map(sev => {
              const count = stats?.by_severity?.[sev] || 0
              const max = Math.max(...Object.values(stats?.by_severity || {0:1}) as number[])
              const pct = max > 0 ? (count / max) * 100 : 0
              
              return (
                <div key={sev}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-400 uppercase">{sev}</span>
                    <span className="text-white font-mono">{count}</span>
                  </div>
                  <div className="w-full bg-gray-800 rounded-full h-2">
                    <div className={`h-2 rounded-full ${sev === 'critical' ? 'bg-red-500' : sev === 'high' ? 'bg-orange-500' : sev === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'}`} style={{ width: `${pct}%` }}></div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        <div className="glass-card p-6 flex flex-col justify-center items-center text-center">
          <span className="text-4xl mb-4 block">📈</span>
          <h2 className="text-xl font-semibold text-white mb-2">Advanced Prometheus Metrics</h2>
          <p className="text-gray-400 max-w-sm mx-auto mb-4 text-sm">
            This dashboard consumes REST endpoints. For deep hardware-level tracking, Kafka offset lags, and memory profiles:
          </p>
          <a href="http://localhost:3001" target="_blank" rel="noreferrer" className="px-6 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-600 rounded-lg text-white font-medium transition-colors text-sm">
            Open Full Grafana APM
          </a>
        </div>
      </div>
    </div>
  )
}
