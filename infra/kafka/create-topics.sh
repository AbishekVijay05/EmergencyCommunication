#!/bin/bash
# =============================================================================
# Create Kafka (Redpanda) topics for the Emergency Communication System
# =============================================================================

set -e

BROKER="${KAFKA_BOOTSTRAP_SERVERS:-redpanda:9092}"

echo "Waiting for Redpanda to be ready..."
until rpk cluster info --brokers "$BROKER" 2>/dev/null; do
    echo "Redpanda not ready yet, retrying in 2s..."
    sleep 2
done

echo "Creating Kafka topics..."

# Incident events from edge nodes
rpk topic create incident-events \
    --brokers "$BROKER" \
    --partitions 4 \
    --replicas 1 \
    --config retention.ms=604800000 \
    2>/dev/null || echo "Topic incident-events already exists"

# Prediction results from ML/rules engine
rpk topic create prediction-events \
    --brokers "$BROKER" \
    --partitions 2 \
    --replicas 1 \
    --config retention.ms=604800000 \
    2>/dev/null || echo "Topic prediction-events already exists"

# Protocol execution and response actions
rpk topic create response-events \
    --brokers "$BROKER" \
    --partitions 2 \
    --replicas 1 \
    --config retention.ms=604800000 \
    2>/dev/null || echo "Topic response-events already exists"

# Audit trail for all system activity
rpk topic create audit-events \
    --brokers "$BROKER" \
    --partitions 2 \
    --replicas 1 \
    --config retention.ms=2592000000 \
    2>/dev/null || echo "Topic audit-events already exists"

# Message delivery events
rpk topic create message-events \
    --brokers "$BROKER" \
    --partitions 4 \
    --replicas 1 \
    --config retention.ms=604800000 \
    2>/dev/null || echo "Topic message-events already exists"

echo "All topics created successfully!"
rpk topic list --brokers "$BROKER"
