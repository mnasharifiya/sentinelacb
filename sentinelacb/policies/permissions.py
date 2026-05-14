from __future__ import annotations
from typing import Set, List
from ..core.models import ActionEvent, EnforcementDecision

class PermissionEngine:
    def __init__(self, allowed: Set[str], high_risk: Set[str], denied_prefixes: List[str]):
        self.allowed = allowed
        self.high_risk = high_risk
        self.denied_prefixes = denied_prefixes

    def evaluate(self, event: ActionEvent) -> EnforcementDecision:
        if any(event.action_type.startswith(p) for p in self.denied_prefixes):
            return EnforcementDecision(decision="DENY", risk_score=1.0, confidence=1.0, reason="Policy violation: denied prefix", layer_triggered="Layer1_Permission")
        if event.action_type not in self.allowed and event.action_type not in self.high_risk:
            return EnforcementDecision(decision="DENY", risk_score=0.9, confidence=0.95, reason="Action out of permitted scope", layer_triggered="Layer1_Permission")
        if event.action_type in self.high_risk:
            return EnforcementDecision(decision="HITL_PENDING", risk_score=0.7, confidence=0.85, reason="High-risk action requires human approval", layer_triggered="Layer1_Permission")
        return EnforcementDecision(decision="ALLOW", risk_score=0.1, confidence=0.99, reason="Within permitted scope", layer_triggered="Layer1_Permission")