from __future__ import annotations
from ..core.models import ActionEvent, EnforcementDecision

class SafeStateController:
    def __init__(self):
        self.active = False
        self.allowed_passive_actions = {"read_sensor", "log_status", "check_health"}

    def activate(self):
        self.active = True

    def reset(self):
        self.active = False

    def evaluate(self, event: ActionEvent, decision: EnforcementDecision) -> EnforcementDecision:
        if self.active and event.action_type not in self.allowed_passive_actions:
            decision.decision = "DENY"
            decision.reason = "System in Safe State S: all non-passive write/network actions revoked"
            decision.risk_score = 0.0
            decision.confidence = 1.0
            decision.layer_triggered = "Layer4_SafeState"
        return decision