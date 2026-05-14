from __future__ import annotations
import time
from typing import Dict, Any
from ..core.models import ActionEvent, EnforcementDecision
from ..policies.permissions import PermissionEngine
from ..monitoring.behavioral import BehavioralMonitor
from ..approval.hitl_gate import HITLGateway
from ..enforcement.safestate import SafeStateController
from ..logging.audit import AuditChain
from ..core.risk_engine import RiskScoringEngine

class EnforcementMiddleware:
    def __init__(self, permissions: PermissionEngine, monitor: BehavioralMonitor,
                 hitl: HITLGateway, safe_state: SafeStateController, audit: AuditChain,
                 risk_engine: RiskScoringEngine):
        self.permissions = permissions
        self.monitor = monitor
        self.hitl = hitl
        self.safe_state = safe_state
        self.audit = audit
        self.risk_engine = risk_engine

    async def process_action(self, event: ActionEvent, context: Dict[str, Any] = None) -> EnforcementDecision:
        start = time.perf_counter()
        context = context or {}
        
        # Layer 4 Check (Priority 1)
        if self.safe_state.active and event.action_type not in self.safe_state.allowed_passive_actions:
            dec = EnforcementDecision(decision="DENY", risk_score=0.0, confidence=1.0, reason="Safe state active", layer_triggered="Layer4_SafeState")
            self.audit.append(event.action_id, "DENY", 0.0)
            return dec

        # Layer 1: Permission Boundary
        perm_dec = self.permissions.evaluate(event)
        if perm_dec.decision == "DENY":
            perm_dec.latency_us = int((time.perf_counter() - start) * 1e6)
            self.audit.append(event.action_id, "DENY", perm_dec.risk_score)
            return perm_dec

        # Core Risk Scoring
        risk_data = self.risk_engine.compute_base_score(event, context)
        
        # Layer 3: Behavioral & Temporal Accumulation
        beh_dec = self.monitor.evaluate(event, risk_data["base_risk"])
        if beh_dec.decision == "DENY":
            self.safe_state.activate()
            self.audit.append(event.action_id, "SAFE_STATE", beh_dec.risk_score)
            return beh_dec

        # Layer 2: HITL Gate (if flagged)
        if perm_dec.decision == "HITL_PENDING":
            perm_dec.risk_score = self.monitor.state.temporal_risk
            perm_dec.confidence = risk_data["confidence"]
            hitl_dec = await self.hitl.request_approval(event, perm_dec)
            if hitl_dec.decision == "DENY" and "timeout" in hitl_dec.reason.lower():
                self.safe_state.activate()
            hitl_dec.latency_us = int((time.perf_counter() - start) * 1e6)
            self.audit.append(event.action_id, hitl_dec.decision, hitl_dec.risk_score)
            return hitl_dec

        # Default Allow
        final = EnforcementDecision(decision="ALLOW", risk_score=risk_data["base_risk"], confidence=risk_data["confidence"], reason="Passed all layers", latency_us=int((time.perf_counter() - start) * 1e6), layer_triggered="Middleware")
        self.audit.append(event.action_id, "ALLOW", final.risk_score)
        return final