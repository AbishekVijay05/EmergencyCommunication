# 🚀 Emergency Communication System — Command Guide

This document lists the essential commands to run and manage the Edge/Fog Emergency Communication system.

## 🛠 Step 1: Permissions & Environment
Run these once to ensure your user has the correct permissions:
```bash
# Add yourself to docker group (needs password once)
sudo usermod -aG docker abishek
newgrp docker
```

## 🧹 Step 2: Clean Up
Ensure the environment is clean before starting:
```bash
cd ~/repos/EmergencyCommunication
chmod +x run.sh
# Clean up old containers and volumes
docker compose down -v --remove-orphans
```

## 🚦 Step 3: Start Everything (The Full Sequence)
Follow this order to ensure all databases and message buses are ready before the services connect:

```bash
# 1. Start core infrastructure
docker compose up -d postgres redis redpanda

# 2. Wait 15 seconds for health checks to pass
sleep 15

# 3. Start topic setup and admin console
docker compose up -d redpanda-console kafka-setup

# 4. Build and start all backend microservices
docker compose up -d --build gateway auth messaging events prediction dsl-engine project-management

# 5. Start edge/fog simulation nodes
docker compose up -d --build edge-node-1 edge-node-2 fog-node-1 fog-node-2

# 6. Start dashboard and monitoring suite
docker compose up -d --build dashboard prometheus grafana
```

---

## 🏗 Quick Management Commands

| Command | Description |
| :--- | :--- |
| `make up` | Start all 16 services (shortcut) |
| `make status` | Check the health of all containers |
| `make logs` | Follow all service logs |
| `make topics` | List Kafka topics |
| `make clean` | Deep clean all images and volumes |

---

## 🖥 Access Points

| Service | URL | Description |
| :--- | :--- | :--- |
| **Main Dashboard** | [http://localhost:3000](http://localhost:3000) | Live Incident & Command UI |
| **API Gateway Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | Unified API Swagger UI |
| **Grafana** | [http://localhost:3001](http://localhost:3001) | System Metrics (User: `admin` / Pass: `admin`) |
| **Redpanda Console** | [http://localhost:8080](http://localhost:8080) | Live Kafka message inspector |

---

## 🧪 Service Swagger Docs
To interact with specific microservices directly:
*   **Messaging**: [http://localhost:8002/docs](http://localhost:8002/docs)
*   **Events**: [http://localhost:8003/docs](http://localhost:8003/docs)
*   **DSL Engine**: [http://localhost:8005/docs](http://localhost:8005/docs)
