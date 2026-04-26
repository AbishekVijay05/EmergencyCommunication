# Architecture Documentation

## System Overview

The Emergency Edge/Fog Communication System is a three-layer distributed architecture:

### Edge Layer (Simulated via Docker containers)
- **edge-node-1**: Zone Alpha — sensors: temperature, smoke, motion
- **edge-node-2**: Zone Beta — sensors: temperature, network, access

Edge nodes generate simulated sensor data, detect incidents when thresholds are exceeded,
and publish events to Kafka. If Kafka is unavailable, events are buffered in Redis.

### Fog Layer (Simulated via Docker containers)
- **fog-node-1**: Primary coordinator — routes messages, executes protocols, consumes events
- **fog-node-2**: Backup coordinator — standby routing, message queue processing

Fog nodes consume events from Kafka, route messages between edge and cloud layers,
enforce DSL protocols, and coordinate multi-zone incidents.

### Cloud Layer
- **Gateway**: API gateway with JWT auth, reverse proxy, rate limiting
- **Auth Service**: User management, JWT tokens, RSA key exchange
- **Messaging Service**: Encrypted messaging, channels, broadcast, WebSocket
- **Events Service**: EDA pipeline, Kafka consumers, event persistence
- **Prediction Service**: Rule-based incident prediction with escalation
- **DSL Engine**: Lark grammar parser, protocol executor, audit logging
- **Project Management**: WBS and EVA tracking
- **Dashboard**: Next.js real-time monitoring

## Security Architecture

### Encryption
- **AES-256-GCM**: All message content encrypted at rest and in transit
- **RSA-2048**: Key exchange for establishing session keys
- **JWT (HS256)**: Authentication tokens with role-based claims

### RBAC Roles
| Role | Description |
|------|-------------|
| admin | Full system access |
| coordinator | Incident management, protocol execution |
| responder | Messaging, event reporting |
| observer | Read-only access |

## Data Flow

```
Edge Node → Kafka (incident-events) → Fog Node → Prediction Engine
                                                 → DSL Protocol Executor
                                                 → Messaging Service → WebSocket → Dashboard
```

## Event Topics
| Topic | Purpose | Partitions | Retention |
|-------|---------|------------|-----------|
| incident-events | Raw incidents from edge | 4 | 7 days |
| prediction-events | Prediction results | 2 | 7 days |
| response-events | Protocol executions | 2 | 7 days |
| audit-events | System audit trail | 2 | 30 days |
| message-events | Message delivery | 4 | 7 days |
