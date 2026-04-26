# API Documentation

## Authentication

### POST /auth/register
Register a new user.
```json
{ "username": "string", "email": "string", "password": "string", "role": "responder|coordinator|admin|observer" }
```

### POST /auth/login
Authenticate and receive JWT tokens.
```json
{ "username": "string", "password": "string" }
```
Response: `{ "access_token": "...", "refresh_token": "...", "token_type": "bearer", "expires_in": 1800, "role": "..." }`

### POST /auth/refresh
Refresh expired access token.
```json
{ "refresh_token": "string" }
```

### POST /auth/keys/exchange
RSA key exchange for establishing encrypted session.
```json
{ "public_key": "PEM string" }
```

---

## Messaging

### POST /messages/send
Send an encrypted message.
```json
{ "recipient_id": "uuid", "content": "string", "priority": "CRITICAL|HIGH|NORMAL|LOW", "message_type": "direct|channel|broadcast" }
```

### GET /messages/history?limit=50&offset=0
Get message history for the authenticated user.

### POST /messages/broadcast
Send emergency broadcast.
```json
{ "content": "string", "priority": "CRITICAL", "zone": "zone-alpha" }
```

### POST /messages/ack
Acknowledge message delivery.
```json
{ "message_id": "uuid" }
```

### WS /ws/messages?user_id=xxx
WebSocket for real-time messaging.

---

## Channels

### POST /channels
Create an incident channel.
```json
{ "name": "string", "description": "string", "incident_type": "string" }
```

### GET /channels
List active channels.

### POST /channels/{id}/join
Join a channel.

### GET /channels/{id}/messages
Get channel message history.

---

## Events

### POST /events/publish
Publish an event to Kafka.
```json
{ "event_type": "fire_alert|medical_emergency|intrusion_detected|network_failure|evacuation_required", "severity": "critical|high|medium|low", "location": "string", "zone": "string" }
```

### GET /events/history?event_type=...&severity=...&zone=...
Query historical events.

### GET /events/stream
Server-Sent Events stream.

### GET /events/stats
Event statistics by type and severity.

---

## Predictions

### POST /predictions/evaluate
Evaluate an event against rules.

### GET /predictions/latest
Latest predictions.

### GET /predictions/rules
List prediction rules.

### POST /predictions/rules
Create a prediction rule.

---

## Protocols (DSL)

### POST /protocols/parse
Parse DSL text.
```json
{ "dsl_source": "WHEN fire_alert severity high\nTHEN\n  notify fire_team\nEND" }
```

### POST /protocols/validate
Validate DSL syntax.

### POST /protocols/execute
Execute a protocol.
```json
{ "protocol_id": "uuid", "trigger_event": {} }
```

### GET /protocols
List saved protocols.

### GET /protocols/{id}/audit
Protocol execution audit log.

---

## Project Management

### GET /project/wbs
Work Breakdown Structure.

### POST /project/wbs/tasks
Create WBS task.

### GET /project/eva
Current EVA metrics (PV, EV, AC, SPI, CPI, SV, CV, EAC).

### POST /project/eva/update
Update WBS item progress.

### GET /project/eva/report
Full EVA report with history.
