# WBS & EVA Documentation

## Work Breakdown Structure (WBS)

| Code | Component | Planned Value ($) | Description |
|------|-----------|-------------------|-------------|
| 1.0 | Messaging Engine | 20,000 | Encrypted messaging, channels, broadcast, WebSocket |
| 2.0 | EDA Pipeline | 15,000 | Kafka event bus, consumers, producers, processors |
| 3.0 | DSL Engine | 15,000 | Lark grammar, parser, executor, audit |
| 4.0 | Security Layer | 10,000 | AES-256, RSA-2048, JWT, RBAC |
| 5.0 | Dashboard | 20,000 | Next.js monitoring, heatmap, chat |
| 6.0 | Monitoring | 10,000 | Prometheus, Grafana, health checks |
| 7.0 | Edge/Fog Simulation | 10,000 | Docker containers, sensor simulation |
| **Total BAC** | | **100,000** | |

## Earned Value Analysis (EVA) Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| PV | Planned budget for scheduled work | Planned Value |
| EV | PV × % Complete | Earned Value |
| AC | Actual money spent | Actual Cost |
| SV | EV - PV | Schedule Variance |
| CV | EV - AC | Cost Variance |
| SPI | EV / PV | Schedule Performance Index |
| CPI | EV / AC | Cost Performance Index |
| EAC | BAC / CPI | Estimate At Completion |

## Interpretation

| SPI/CPI | Status |
|---------|--------|
| ≥ 1.0 | On track or ahead |
| 0.9 - 1.0 | Minor variance |
| 0.7 - 0.9 | At risk |
| < 0.7 | Behind schedule/over budget |

## API Endpoints

- `GET /project/wbs` — View WBS breakdown
- `POST /project/wbs/tasks` — Create/update tasks
- `GET /project/eva` — Current EVA metrics
- `POST /project/eva/update` — Update progress
- `GET /project/eva/report` — Full report with history
