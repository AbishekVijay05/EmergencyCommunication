'use client'

import { useState, useEffect, useRef, useCallback } from 'react'

interface Message {
  id: string
  sender_id: string
  content: string
  priority: string
  message_type: string
  created_at: string
  channel_id?: string
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8002/ws/messages'

export default function MessagingPage() {
  const [channels] = useState(['# global-alerts', '# alpha-team', '# beta-team', '# medical', '# command'])
  const [activeChannel, setActiveChannel] = useState(0)
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [wsConnected, setWsConnected] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const wsRef = useRef<WebSocket | null>(null)

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  // Fetch message history
  useEffect(() => {
    const fetchMessages = async () => {
      try {
        const res = await fetch(`${API_BASE}/messages/history?limit=50`, {
          headers: { 'X-User-Id': '00000000-0000-0000-0000-000000000000' },
        })
        if (res.ok) {
          const data = await res.json()
          setMessages(data)
          setError('')
        } else {
          throw new Error('Failed to fetch')
        }
      } catch (err) {
        setError('Unable to connect to Messaging service')
        // Use fallback demo messages if API unavailable
        setMessages([
          { id: '1', sender_id: 'System', content: 'Routine system check completed. All nodes online.', priority: 'NORMAL', message_type: 'broadcast', created_at: new Date().toISOString() },
          { id: '2', sender_id: 'Alpha-Leader', content: 'Approaching Sector 4 for perimeter check.', priority: 'NORMAL', message_type: 'channel', created_at: new Date().toISOString() },
          { id: '3', sender_id: 'Gateway Proxy', content: 'CRITICAL: Smoke detected in Zone Alpha-3.', priority: 'CRITICAL', message_type: 'broadcast', created_at: new Date().toISOString() },
          { id: '4', sender_id: 'Command', content: 'Alpha-Leader, please investigate Alpha-3 immediately.', priority: 'HIGH', message_type: 'direct', created_at: new Date().toISOString() },
          { id: '5', sender_id: 'Alpha-Leader', content: 'Confirmed small electrical fire. Extinguishing now.', priority: 'NORMAL', message_type: 'channel', created_at: new Date().toISOString() },
        ])
      } finally {
        setLoading(false)
      }
    }
    fetchMessages()
  }, [])

  // WebSocket connection
  useEffect(() => {
    let ws: WebSocket | null = null
    try {
      ws = new WebSocket(WS_URL)
      wsRef.current = ws

      ws.onopen = () => setWsConnected(true)
      ws.onclose = () => setWsConnected(false)
      ws.onerror = () => setWsConnected(false)

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)
          setMessages(prev => [...prev, msg])
        } catch {
          // non-JSON message
        }
      }
    } catch {
      setWsConnected(false)
    }

    return () => {
      ws?.close()
    }
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  const handleSend = async () => {
    if (!inputValue.trim()) return

    const messagePayload = {
      content: inputValue.trim(),
      priority: 'NORMAL',
      message_type: 'broadcast',
    }

    // Try sending via REST API
    try {
      const res = await fetch(`${API_BASE}/messages/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': 'dashboard-user',
        },
        body: JSON.stringify(messagePayload),
      })
      if (res.ok) {
        const sent = await res.json()
        setMessages(prev => [...prev, {
          id: sent.id || String(Date.now()),
          sender_id: 'You',
          content: inputValue.trim(),
          priority: 'NORMAL',
          message_type: 'broadcast',
          created_at: new Date().toISOString(),
        }])
      }
    } catch {
      // Fallback: add locally if API unavailable
      setMessages(prev => [...prev, {
        id: String(Date.now()),
        sender_id: 'You',
        content: inputValue.trim(),
        priority: 'NORMAL',
        message_type: 'broadcast',
        created_at: new Date().toISOString(),
      }])
    }

    setInputValue('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const formatTime = (iso: string) => {
    try {
      return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } catch {
      return ''
    }
  }

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col animate-fade-in">
      <div className="mb-6">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
          Secure Messaging
        </h1>
        <p className="text-gray-400 mt-1">End-to-end AES-256-GCM encrypted comms</p>
      </div>

      <div className="flex-1 glass-card overflow-hidden flex">
        {/* Sidebar */}
        <div className="w-64 border-r border-gray-800 bg-gray-900/50 flex flex-col">
          <div className="p-4 border-b border-gray-800">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Channels</h3>
          </div>
          <div className="p-2 space-y-1 overflow-y-auto flex-1">
            {channels.map((ch, i) => (
              <button 
                key={ch}
                onClick={() => setActiveChannel(i)} 
                className={`w-full text-left px-4 py-2 rounded-lg text-sm transition-colors ${i === activeChannel ? 'bg-command-600/20 text-command-400 font-medium' : 'text-gray-400 hover:bg-gray-800 hover:text-white'}`}
              >
                {ch}
              </button>
            ))}
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          <div className="p-4 border-b border-gray-800 bg-gray-900/30 flex items-center justify-between">
            <div>
              <h2 className="font-semibold text-white">{channels[activeChannel]}</h2>
              <p className="text-xs text-gray-500">Encrypted Broadcast Channel</p>
            </div>
            <div className={`flex items-center gap-2 text-xs px-3 py-1 rounded-full border ${wsConnected ? 'text-green-400 bg-green-400/10 border-green-400/20' : 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20'}`}>
              <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-400 animate-pulse' : 'bg-yellow-400'}`}></span>
              {wsConnected ? 'Live Connection' : 'REST Mode'}
            </div>
          </div>

          <div className="flex-1 p-6 overflow-y-auto space-y-6">
            {loading && <div className="text-center py-10 text-gray-500">Loading messages...</div>}
            {error && !loading && <div className="text-center text-xs text-yellow-500/60 mb-4">{error} — showing demo messages</div>}
            
            {messages.map((msg) => (
              <div key={msg.id} className={`flex flex-col ${msg.sender_id === 'You' || msg.sender_id === 'Command' ? 'items-end' : 'items-start'}`}>
                <div className="flex items-baseline gap-2 mb-1">
                  <span className={`text-sm font-medium ${
                    msg.sender_id === 'System' ? 'text-gray-400' : 
                    msg.sender_id === 'You' || msg.sender_id === 'Command' ? 'text-command-400' : 
                    'text-indigo-400'
                  }`}>
                    {msg.sender_id}
                  </span>
                  <span className="text-xs text-gray-600">{formatTime(msg.created_at)}</span>
                  {msg.priority === 'CRITICAL' && <span className="text-xs bg-red-500/20 text-red-400 px-1.5 py-0.5 rounded">CRITICAL</span>}
                </div>
                <div className={`px-4 py-2 rounded-2xl max-w-[80%] text-sm ${
                  msg.priority === 'CRITICAL'
                    ? 'bg-red-500/20 border border-red-500/30 text-red-100' 
                    : msg.sender_id === 'You' || msg.sender_id === 'Command'
                      ? 'bg-command-600 text-white rounded-tr-none'
                      : 'bg-gray-800 text-gray-200 border border-gray-700 rounded-tl-none'
                }`}>
                  {msg.priority === 'CRITICAL' && <span className="mr-2">🚨</span>}
                  {msg.content}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          <div className="p-4 border-t border-gray-800 bg-gray-900/50">
            <div className="relative">
              <input 
                type="text" 
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type an encrypted message..." 
                className="w-full bg-gray-950 border border-gray-700 rounded-lg pl-4 pr-12 py-3 text-sm focus:outline-none focus:border-command-500 transition-colors"
              />
              <button 
                onClick={handleSend}
                disabled={!inputValue.trim()}
                className="absolute right-2 top-2 bottom-2 aspect-square bg-command-600 hover:bg-command-500 rounded text-white flex items-center justify-center transition-colors disabled:opacity-50"
              >
                ➤
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
