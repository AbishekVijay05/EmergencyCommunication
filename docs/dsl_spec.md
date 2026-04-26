# Emergency Protocol DSL Specification

## Overview

The Emergency Protocol DSL is a domain-specific language for defining automated emergency response workflows.
It uses a WHEN-THEN-END structure to map triggers and conditions to executable actions.

## Grammar (LALR(1) via Lark)

```
protocol := "WHEN" <trigger> <condition>* "THEN" <action>+ "END"
trigger  := EVENT_TYPE
condition := "severity" SEVERITY | "zone" IDENTIFIER | "count" ">" NUMBER
action   := "notify" ID | "lock" ID | "dispatch" ID | "alert" ID | "evacuate" ID | "broadcast" MSG | "log" MSG
```

## Event Types

| Event Type | Description |
|-----------|-------------|
| fire_alert | Fire detected |
| medical_emergency | Medical incident |
| intrusion_detected | Unauthorized access |
| network_failure | Network connectivity loss |
| evacuation_required | Evacuation trigger |

## Severity Levels

| Level | Priority |
|-------|----------|
| critical | Immediate response |
| high | Urgent response |
| medium | Standard response |
| low | Monitoring only |

## Actions

| Action | Syntax | Description |
|--------|--------|-------------|
| notify | `notify <team>` | Send notification to team |
| lock | `lock <zone>` | Lock down a zone |
| dispatch | `dispatch <resource>` | Dispatch emergency resource |
| alert | `alert <authority>` | Alert an authority |
| evacuate | `evacuate <zone>` | Initiate evacuation |
| broadcast | `broadcast "message"` | Emergency broadcast |
| log | `log "message"` | Log an event |

## Examples

### Fire Response
```
WHEN fire_alert severity high
THEN
  notify fire_team
  lock building_zone_3
  dispatch ambulance
  alert police
  broadcast "Fire alert: evacuate zone 3"
END
```

### Medical Emergency
```
WHEN medical_emergency severity critical
THEN
  dispatch medical_team
  notify hospital
  alert paramedics
  log "Critical medical emergency dispatched"
END
```

### Multi-Protocol File
```
WHEN fire_alert severity critical
THEN
  evacuate all_zones
  notify all_teams
  dispatch fire_brigade
  alert city_emergency
END

WHEN intrusion_detected severity high
THEN
  lock affected_zone
  alert security_team
  notify police
  broadcast "Security breach detected"
END
```
