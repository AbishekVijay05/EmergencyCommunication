# =============================================================================
# Protocol Executor — Execute parsed DSL protocols
# =============================================================================
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any


class ActionRegistry:
    """Registry of executable actions for DSL protocols."""

    def __init__(self):
        self._actions: dict[str, callable] = {
            "notify": self._action_notify,
            "lock": self._action_lock,
            "dispatch": self._action_dispatch,
            "alert": self._action_alert,
            "evacuate": self._action_evacuate,
            "broadcast": self._action_broadcast,
            "log": self._action_log,
        }
        self._execution_log: list[dict] = []

    async def execute_action(self, action_type: str, target: str) -> dict:
        """Execute a single protocol action."""
        handler = self._actions.get(action_type)
        if not handler:
            return {"status": "error", "error": f"Unknown action: {action_type}"}

        result = await handler(target)
        self._execution_log.append({
            "action": action_type,
            "target": target,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return result

    async def _action_notify(self, target: str) -> dict:
        print(f"📢 NOTIFY: Sending notification to {target}")
        return {"action": "notify", "target": target, "status": "sent"}

    async def _action_lock(self, target: str) -> dict:
        print(f"🔒 LOCK: Locking zone {target}")
        return {"action": "lock", "target": target, "status": "locked"}

    async def _action_dispatch(self, target: str) -> dict:
        print(f"🚑 DISPATCH: Dispatching {target}")
        return {"action": "dispatch", "target": target, "status": "dispatched"}

    async def _action_alert(self, target: str) -> dict:
        print(f"🚨 ALERT: Alerting {target}")
        return {"action": "alert", "target": target, "status": "alerted"}

    async def _action_evacuate(self, target: str) -> dict:
        print(f"🏃 EVACUATE: Evacuating {target}")
        return {"action": "evacuate", "target": target, "status": "evacuation_initiated"}

    async def _action_broadcast(self, target: str) -> dict:
        print(f"📡 BROADCAST: {target}")
        return {"action": "broadcast", "message": target, "status": "broadcasted"}

    async def _action_log(self, target: str) -> dict:
        print(f"📝 LOG: {target}")
        return {"action": "log", "message": target, "status": "logged"}

    def get_log(self) -> list[dict]:
        return self._execution_log

    def clear_log(self):
        self._execution_log.clear()


class ProtocolExecutor:
    """Execute parsed emergency protocols."""

    def __init__(self):
        self.registry = ActionRegistry()

    async def execute(self, protocol: dict, context: dict = None) -> dict:
        """Execute a parsed protocol definition.

        Args:
            protocol: Parsed protocol dict with trigger, conditions, actions
            context: Optional event context for condition evaluation

        Returns:
            Execution result with timing and action results
        """
        start = time.perf_counter()
        results = []

        # Check conditions if context provided
        if context:
            if not self._check_conditions(protocol.get("conditions", []), context):
                return {
                    "status": "skipped",
                    "reason": "conditions not met",
                    "execution_time_ms": 0,
                }

        # Execute actions
        for action in protocol.get("actions", []):
            result = await self.registry.execute_action(
                action["type"],
                action["target"],
            )
            results.append(result)

        elapsed = (time.perf_counter() - start) * 1000

        return {
            "status": "completed",
            "trigger": protocol.get("trigger"),
            "actions_executed": results,
            "execution_time_ms": round(elapsed, 2),
        }

    def _check_conditions(self, conditions: list[dict], context: dict) -> bool:
        """Check if protocol conditions are met."""
        for cond in conditions:
            cond_type = cond.get("type", "")
            cond_value = cond.get("value", "")

            if cond_type == "severity":
                if context.get("severity", "") != cond_value:
                    return False
            elif cond_type == "zone":
                if context.get("zone", "") != cond_value:
                    return False

        return True
