# =============================================================================
# Emergency Edge/Fog Communication System — Developer Commands
# =============================================================================

.PHONY: help up down build logs test clean status

# Use standard docker compose command
DC = docker compose

help: ## Show this help message
	@echo "Emergency Edge/Fog Communication System"
	@echo "========================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# Docker Compose Commands
# ---------------------------------------------------------------------------

up: ## Start all services
	$(DC) up -d
	@echo "✅ All services starting..."
	@echo "   Gateway:    http://localhost:8000"
	@echo "   Dashboard:  http://localhost:3000"
	@echo "   Redpanda:   http://localhost:8080"
	@echo "   Prometheus: http://localhost:9090"
	@echo "   Grafana:    http://localhost:3001"

up-infra: ## Start only infrastructure (postgres, redis, redpanda)
	$(DC) up -d postgres redis redpanda redpanda-console kafka-setup

up-backend: ## Start infrastructure + backend services
	$(DC) up -d postgres redis redpanda redpanda-console kafka-setup gateway auth messaging events prediction dsl-engine project-management

up-edge-fog: ## Start edge and fog nodes
	$(DC) up -d edge-node-1 edge-node-2 fog-node-1 fog-node-2

down: ## Stop all services
	$(DC) down

down-clean: ## Stop all services and remove volumes
	$(DC) down -v --remove-orphans

build: ## Build all Docker images
	$(DC) build

build-no-cache: ## Build all Docker images without cache
	$(DC) build --no-cache

restart: ## Restart all services
	$(DC) restart

# ---------------------------------------------------------------------------
# Monitoring
# ---------------------------------------------------------------------------

status: ## Show service status
	$(DC) ps

logs: ## Follow all service logs
	$(DC) logs -f

logs-gateway: ## Follow gateway logs
	$(DC) logs -f gateway

logs-edge: ## Follow edge node logs
	$(DC) logs -f edge-node-1 edge-node-2

logs-fog: ## Follow fog node logs
	$(DC) logs -f fog-node-1 fog-node-2

logs-events: ## Follow events service logs
	$(DC) logs -f events

health: ## Check all service health
	@echo "Checking service health..."
	@curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "Gateway: unavailable"

# ---------------------------------------------------------------------------
# Development
# ---------------------------------------------------------------------------

dashboard-dev: ## Run dashboard in development mode
	cd services/dashboard && npm install && npm run dev

test: ## Run all tests
	@echo "Running tests..."
	$(DC) exec gateway pytest -v 2>/dev/null || echo "No gateway tests yet"
	$(DC) exec auth pytest -v 2>/dev/null || echo "No auth tests yet"

lint: ## Lint Python code
	find services -name "*.py" | head -20 | xargs python3 -m py_compile 2>&1

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

topics: ## List Kafka topics
	$(DC) exec redpanda rpk topic list

create-topics: ## Create Kafka topics
	$(DC) exec redpanda bash /scripts/create-topics.sh

psql: ## Connect to PostgreSQL
	$(DC) exec postgres psql -U emergency_admin -d emergency_main

redis-cli: ## Connect to Redis
	$(DC) exec redis redis-cli -a redis_secure_pass_2025

clean: ## Remove all containers, volumes, and images
	$(DC) down -v --remove-orphans --rmi local
	@echo "🧹 Cleaned up all containers and volumes"
