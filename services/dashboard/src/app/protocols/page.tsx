'use client'

import { useState } from 'react'

export default function ProtocolsPage() {
  const [dslInput, setDslInput] = useState(
`WHEN fire_alert severity high
THEN
  notify fire_team
  lock building_zone_3
  dispatch ambulance
END`
  )

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
          Emergency Protocols (DSL)
        </h1>
        <p className="text-gray-400 mt-1">Define and execute automated response logic</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="glass-card p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-white">Live Editor</h2>
              <span className="text-xs bg-purple-500/20 text-purple-400 px-2 py-1 rounded border border-purple-500/30">LALR Parser Active</span>
            </div>
            <textarea 
              value={dslInput}
              onChange={(e) => setDslInput(e.target.value)}
              className="w-full h-64 bg-gray-950 text-gray-300 font-mono text-sm p-4 rounded-lg border border-gray-800 focus:outline-none focus:border-purple-500/50 transition-colors resize-none"
              spellCheck="false"
            />
            <div className="mt-4 flex justify-end gap-3">
              <button className="px-4 py-2 border border-gray-700 hover:bg-gray-800 text-gray-300 rounded-lg transition-colors text-sm">
                Validate Syntax
              </button>
              <button className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg transition-colors text-sm font-medium shadow-[0_0_15px_rgba(147,51,234,0.3)]">
                Deploy Protocol
              </button>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="glass-card p-6 h-full">
            <h2 className="text-lg font-semibold text-white mb-4">Active Protocols</h2>
            <div className="space-y-3">
              {[
                { name: 'Fire Response Alpha', trigger: 'fire_alert', actions: 4, status: 'Active' },
                { name: 'Medical Dispatch', trigger: 'medical_emergency', actions: 3, status: 'Active' },
                { name: 'Zone Lockdown', trigger: 'intrusion_detected', actions: 5, status: 'Standby' },
                { name: 'Seismic Protocol', trigger: 'earthquake', actions: 8, status: 'Active' },
              ].map(p => (
                <div key={p.name} className="flex items-center justify-between p-4 bg-gray-900/50 border border-gray-800 rounded-lg">
                  <div>
                    <h3 className="text-sm font-medium text-white">{p.name}</h3>
                    <p className="text-xs text-gray-500 mt-1">ON: <span className="text-command-400 font-mono">{p.trigger}</span> → {p.actions} actions</p>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className={`text-xs px-2 py-1 rounded-full ${p.status === 'Active' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                      {p.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
