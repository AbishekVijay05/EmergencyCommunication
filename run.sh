#!/bin/bash
# =============================================================================
# Emergency Communication System â€” Launch Script
# Handles Docker group permissions automatically
# =============================================================================

set -e

DC="docker compose"

# Check if we need sg docker
if ! docker info >/dev/null 2>&1; then
    echo "âš ï¸  Docker permission issue detected. Using 'sg docker'..."
    DC="sg docker -c 'docker compose'"
fi

case "${1:-up}" in
    up)
        echo "ðŸš€ Starting Emergency Communication System..."
        echo ""

        echo "ðŸ“¦ Step 1: Starting infrastructure (PostgreSQL, Redis, Redpanda)..."
        eval $DC up -d postgres redis redpanda
        
        echo "â³ Waiting for infrastructure to be healthy..."
        sleep 15

        echo "ðŸ“¦ Step 2: Setting up Kafka topics..."
        eval $DC up -d redpanda-console kafka-setup

        sleep 5

        echo "ðŸ“¦ Step 3: Building and starting application services..."
        eval $DC up -d --build gateway auth messaging events prediction dsl-engine project-management

        echo "ðŸ“¦ Step 4: Starting edge and fog nodes..."
        eval $DC up -d --build edge-node-1 edge-node-2 fog-node-1 fog-node-2

        echo "ðŸ“¦ Step 5: Starting dashboard and monitoring..."
        eval $DC up -d --build dashboard prometheus grafana

        echo ""
        echo "âœ… All services starting!"
        echo "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•"
        echo "  Gateway API:    http://localhost:8000/docs"
        echo "  Dashboard:      http://localhost:3000"
        echo "  Redpanda UI:    http://localhost:8080"
        echo "  Prometheus:     http://localhost:9090"
        echo "  Grafana:        http://localhost:3001"
        echo "â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•"
        echo ""
        echo "Run './run.sh status' to check service health"
        ;;
    
    down)
        echo "ðŸ›‘ Stopping all services..."
        eval $DC down
        ;;
    
    status)
        echo "ðŸ“Š Service Status:"
        eval $DC ps
        ;;
    
    logs)
        eval $DC logs -f ${@:2}
        ;;
    
    build)
        echo "ðŸ”¨ Building all images..."
        eval $DC build
        ;;
    
    clean)
        echo "ðŸ§¹ Cleaning up everything..."
        eval $DC down -v --remove-orphans --rmi local
        ;;
    
    *)
        echo "Usage: ./run.sh [up|down|status|logs|build|clean]"
        ;;
esac
