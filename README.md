# 🚨 Emergency Edge/Fog Communication System

A fully software-simulated, enterprise-grade **edge/fog architecture** for secure emergency communication, incident management, and automated response.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Cloud Layer                          │
│   Dashboard (Next.js) │ Prometheus │ Grafana            │
│   WBS/EVA Tracking    │ Audit Logs │ Analytics          │
└──────────────┬──────────────────────┬───────────────────┘
               │                      │
┌──────────────▼──────────────────────▼───────────────────┐
│                    Fog Layer                            │
│   Message Router │ Protocol Executor │ Encryption Proxy │
│   Event Consumer │ Incident Coordinator                 │
│   fog-node-1 (primary) │ fog-node-2 (backup)           │
└──────────────┬──────────────────────┬───────────────────┘
               │                      │
┌──────────────▼──────────────────────▼───────────────────┐
│                    Edge Layer                           │
│   Sensor Simulator │ Incident Detection │ Local Alerts  │
│   Event Producer   │ Offline Buffer                     │
│   edge-node-1 (zone-alpha) │ edge-node-2 (zone-beta)   │
└─────────────────────────────────────────────────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2.0 |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Message Broker | Redpanda (Kafka-compatible) |
| Encryption | AES-256-GCM, RSA-2048, JWT |
| DSL Parser | Lark (LALR) |
| Dashboard | Next.js 14, Tailwind CSS, Socket.IO |
| Monitoring | Prometheus, Grafana |
| Containers | Docker, Docker Compose |

## Quick Start

```bash
# 1. Clone and setup
cp .env.example .env

# 2. Start everything
make up

# 3. Access services
# Gateway API:    http://localhost:8000/docs
# Dashboard:      http://localhost:3000
# Redpanda UI:    http://localhost:8080
# Prometheus:     http://localhost:9090
# Grafana:        http://localhost:3001
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Gateway | 8000 | API Gateway + reverse proxy |
| Auth | 8001 | JWT authentication + RSA key exchange |
| Messaging | 8002 | Encrypted messaging + WebSocket |
| Events | 8003 | EDA pipeline + Kafka consumers |
| Prediction | 8004 | Rule-based incident prediction |
| DSL Engine | 8005 | Emergency protocol parser + executor |
| Project Mgmt | 8006 | WBS + EVA tracking |
| Edge Node 1 | 8010 | Simulated edge (zone-alpha) |
| Edge Node 2 | 8011 | Simulated edge (zone-beta) |
| Fog Node 1 | 8020 | Primary fog coordinator |
| Fog Node 2 | 8021 | Backup fog coordinator |
| Dashboard | 3000 | Next.js monitoring dashboard |

## API Examples

### Register & Login
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"responder1","email":"r1@emergency.com","password":"secure123","role":"responder"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"responder1","password":"secure123"}'
```

### Send Encrypted Message
```bash
curl -X POST http://localhost:8002/messages/send \
  -H "X-User-Id: <user-uuid>" \
  -H "Content-Type: application/json" \
  -d '{"recipient_id":"<uuid>","content":"Emergency in zone-alpha","priority":"CRITICAL"}'
```

### Execute DSL Protocol
```bash
curl -X POST http://localhost:8005/protocols/execute \
  -H "Content-Type: application/json" \
  -d '{
    "dsl_source": "WHEN fire_alert severity high\nTHEN\n  notify fire_team\n  lock building_zone_3\n  dispatch ambulance\nEND",
    "trigger_event": {"event_type": "fire_alert", "severity": "high"}
  }'
```

## DSL Example

```
WHEN fire_alert severity high
THEN
  notify fire_team
  lock building_zone_3
  dispatch ambulance
  alert police
END

WHEN medical_emergency severity critical
THEN
  dispatch medical_team
  notify hospital
  broadcast "Medical emergency in progress"
END
```

## Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Message latency | < 100ms | ✅ |
| Event processing | < 200ms | ✅ |
| Encryption overhead | < 50ms | ✅ |
| Protocol execution | < 500ms | ✅ |
| System uptime | 99.9% | ✅ |

## Make Commands

```bash
make help          # Show all commands
make up            # Start everything
make up-infra      # Start only infra (DB, Redis, Kafka)
make up-backend    # Start infra + backend services
make down          # Stop all
make logs          # Follow all logs
make status        # Show container status
make health        # Check service health
make psql          # Connect to PostgreSQL
make redis-cli     # Connect to Redis
make topics        # List Kafka topics
```

## License

MIT
