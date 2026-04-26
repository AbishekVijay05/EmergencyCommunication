#!/bin/bash
# =============================================================================
# Emergency Communication System — Launch Script
# Handles Docker group permissions automatically
# =============================================================================

set -e

DC="docker compose"

# Check if we need sg docker
if ! docker info >/dev/null 2>&1; then
    echo "⚠️  Docker permission issue detected. Using 'sg docker'..."
    DC="sg docker -c 'docker compose'"
fi

case "${1:-up}" in
    up)
        echo "🚀 Starting Emergency Communication System..."
        echo ""

        echo "📦 Step 1: Starting infrastructure (PostgreSQL, Redis, Redpanda)..."
        eval $DC up -d postgres redis redpanda
        
        echo "⏳ Waiting for infrastructure to be healthy..."
        sleep 15

        echo "📦 Step 2: Setting up Kafka topics..."
        eval $DC up -d redpanda-console kafka-setup

        sleep 5

        echo "📦 Step 3: Building and starting application services..."
        eval $DC up -d --build gateway auth messaging events prediction dsl-engine project-management

        echo "📦 Step 4: Starting edge and fog nodes..."
        eval $DC up -d --build edge-node-1 edge-node-2 fog-node-1 fog-node-2

        echo "📦 Step 5: Starting dashboard and monitoring..."
        eval $DC up -d --build dashboard prometheus grafana

        echo ""
        echo "✅ All services starting!"
        echo "════════════════════════════════════════"
        echo "  Gateway API:    http://localhost:8000/docs"
        echo "  Dashboard:      http://localhost:3000"
        echo "  Redpanda UI:    http://localhost:8080"
        echo "  Prometheus:     http://localhost:9090"
        echo "  Grafana:        http://localhost:3001"
        echo "════════════════════════════════════════"
        echo ""
        echo "Run './run.sh status' to check service health"
        ;;
    
    down)
        echo "🛑 Stopping all services..."
        eval $DC down
        ;;
    
    status)
        echo "📊 Service Status:"
        eval $DC ps
        ;;
    
    logs)
        eval $DC logs -f ${@:2}
        ;;
    
    build)
        echo "🔨 Building all images..."
        eval $DC build
        ;;
    
    clean)
        echo "🧹 Cleaning up everything..."
        eval $DC down -v --remove-orphans --rmi local
        ;;
    
    *)
        echo "Usage: ./run.sh [up|down|status|logs|build|clean]"
        ;;
esac
