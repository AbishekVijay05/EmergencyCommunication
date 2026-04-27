-- =============================================================================
-- Emergency Edge/Fog Communication System
-- PostgreSQL Multi-Database Initialization
-- =============================================================================

-- Create databases for each microservice
CREATE DATABASE emergency_auth;
CREATE DATABASE emergency_messaging;
CREATE DATABASE emergency_events;
CREATE DATABASE emergency_prediction;
CREATE DATABASE emergency_dsl;
CREATE DATABASE emergency_project;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE emergency_auth TO emergency_admin;
GRANT ALL PRIVILEGES ON DATABASE emergency_messaging TO emergency_admin;
GRANT ALL PRIVILEGES ON DATABASE emergency_events TO emergency_admin;
GRANT ALL PRIVILEGES ON DATABASE emergency_prediction TO emergency_admin;
GRANT ALL PRIVILEGES ON DATABASE emergency_dsl TO emergency_admin;
GRANT ALL PRIVILEGES ON DATABASE emergency_project TO emergency_admin;

-- =============================================================================
-- Auth Database Schema
-- =============================================================================
\c emergency_auth;
GRANT ALL ON SCHEMA public TO emergency_admin;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'responder',
    public_key TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- =============================================================================
-- Messaging Database Schema
-- =============================================================================
\c emergency_messaging;
GRANT ALL ON SCHEMA public TO emergency_admin;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE channels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    incident_type VARCHAR(50),
    created_by UUID NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE channel_members (
    channel_id UUID REFERENCES channels(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    role VARCHAR(20) DEFAULT 'member',
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (channel_id, user_id)
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID NOT NULL,
    recipient_id UUID,
    channel_id UUID REFERENCES channels(id) ON DELETE SET NULL,
    encrypted_content TEXT NOT NULL,
    priority VARCHAR(10) DEFAULT 'NORMAL' CHECK (priority IN ('CRITICAL', 'HIGH', 'NORMAL', 'LOW')),
    message_type VARCHAR(20) DEFAULT 'direct' CHECK (message_type IN ('direct', 'channel', 'broadcast')),
    iv TEXT NOT NULL,
    tag TEXT NOT NULL,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMPTZ,
    delivered BOOLEAN DEFAULT FALSE,
    delivered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_messages_sender ON messages(sender_id);
CREATE INDEX idx_messages_recipient ON messages(recipient_id);
CREATE INDEX idx_messages_channel ON messages(channel_id);
CREATE INDEX idx_messages_priority ON messages(priority);
CREATE INDEX idx_messages_created ON messages(created_at DESC);

-- =============================================================================
-- Events Database Schema
-- =============================================================================
\c emergency_events;
GRANT ALL ON SCHEMA public TO emergency_admin;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id VARCHAR(100) UNIQUE NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    location VARCHAR(100),
    zone VARCHAR(50),
    source_node VARCHAR(50),
    payload JSONB DEFAULT '{}',
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_severity ON events(severity);
CREATE INDEX idx_events_zone ON events(zone);
CREATE INDEX idx_events_created ON events(created_at DESC);
CREATE INDEX idx_events_payload ON events USING GIN(payload);

CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id VARCHAR(100),
    actor_id UUID,
    details JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_action ON audit_log(action);
CREATE INDEX idx_audit_created ON audit_log(created_at DESC);

-- =============================================================================
-- Prediction Database Schema
-- =============================================================================
\c emergency_prediction;
GRANT ALL ON SCHEMA public TO emergency_admin;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE prediction_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    condition_expr TEXT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    action_params JSONB DEFAULT '{}',
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id UUID REFERENCES prediction_rules(id),
    event_id VARCHAR(100),
    prediction_type VARCHAR(50) NOT NULL,
    confidence FLOAT DEFAULT 0.0,
    result JSONB DEFAULT '{}',
    escalated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_predictions_type ON predictions(prediction_type);
CREATE INDEX idx_predictions_created ON predictions(created_at DESC);

-- Insert default prediction rules
INSERT INTO prediction_rules (name, description, condition_expr, action_type, priority) VALUES
('High Severity Repeat', 'Trigger critical when high severity events repeat', 'severity == "high" AND repeated_events > 3', 'trigger_critical_incident', 10),
('Fire Auto-Evacuate', 'Auto evacuate on high/critical fire', 'event_type == "fire_alert" AND severity IN ("high", "critical")', 'auto_evacuate', 20),
('Event Storm', 'Escalate when too many events in short time', 'event_count_last_5min > 10', 'escalate_to_coordinator', 15),
('Medical Critical', 'Immediate dispatch on critical medical', 'event_type == "medical_emergency" AND severity == "critical"', 'dispatch_medical_team', 25),
('Intrusion + Network', 'Compound alert: intrusion with network failure', 'event_type == "intrusion_detected" AND concurrent_network_failure == true', 'lockdown_zone', 30);

-- =============================================================================
-- DSL Database Schema
-- =============================================================================
\c emergency_dsl;
GRANT ALL ON SCHEMA public TO emergency_admin;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE protocols (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    dsl_source TEXT NOT NULL,
    compiled JSONB,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE protocol_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    protocol_id UUID REFERENCES protocols(id),
    trigger_event_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    actions_executed JSONB DEFAULT '[]',
    execution_time_ms INTEGER,
    error_message TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_executions_protocol ON protocol_executions(protocol_id);
CREATE INDEX idx_executions_status ON protocol_executions(status);

-- =============================================================================
-- Project Management Database Schema
-- =============================================================================
\c emergency_project;
GRANT ALL ON SCHEMA public TO emergency_admin;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE wbs_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID REFERENCES wbs_items(id),
    code VARCHAR(20) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    planned_value DECIMAL(12,2) DEFAULT 0,
    actual_cost DECIMAL(12,2) DEFAULT 0,
    earned_value DECIMAL(12,2) DEFAULT 0,
    percent_complete DECIMAL(5,2) DEFAULT 0,
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'not_started' CHECK (status IN ('not_started', 'in_progress', 'completed', 'blocked')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE eva_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_date DATE NOT NULL,
    total_pv DECIMAL(12,2) DEFAULT 0,
    total_ev DECIMAL(12,2) DEFAULT 0,
    total_ac DECIMAL(12,2) DEFAULT 0,
    spi DECIMAL(6,4),
    cpi DECIMAL(6,4),
    sv DECIMAL(12,2),
    cv DECIMAL(12,2),
    eac DECIMAL(12,2),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default WBS structure
INSERT INTO wbs_items (code, name, planned_value, status) VALUES
('1.0', 'Messaging Engine', 20000.00, 'not_started'),
('2.0', 'EDA Pipeline', 15000.00, 'not_started'),
('3.0', 'DSL Engine', 15000.00, 'not_started'),
('4.0', 'Security Layer', 10000.00, 'not_started'),
('5.0', 'Dashboard', 20000.00, 'not_started'),
('6.0', 'Monitoring', 10000.00, 'not_started'),
('7.0', 'Edge/Fog Simulation', 10000.00, 'not_started');
