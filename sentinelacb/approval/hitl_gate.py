from __future__ import annotations
import asyncio
from typing import Dict
from ..core.models import ActionEvent, EnforcementDecision

class HITLGateway:
    def __init__(self, timeout_sec: float = 15.0):
        self.timeout_sec = timeout_sec
        self.pending_requests: Dict[str, asyncio.Future] = {}

    async def request_approval(self, event: ActionEvent, decision: EnforcementDecision) -> EnforcementDecision:
        req_id = f"{event.source_agent}:{event.action_id}"
        decision.decision = "HITL_PENDING"
        decision.reason = "Approval requested via secure out-of-band channel"
        decision.layer_triggered = "Layer2_HITL"
        
        future = asyncio.get_running_loop().create_future()
        self.pending_requests[req_id] = future

        try:
            approved = await asyncio.wait_for(future, timeout=self.timeout_sec)
            if approved:
                decision.decision = "ALLOW"
                decision.reason = "Human operator explicitly approved"
                decision.confidence = 0.95
            else:
                decision.decision = "DENY"
                decision.reason = "Human operator explicitly rejected"
        except asyncio.TimeoutError:
            decision.decision = "DENY"
            decision.reason = "Approval timeout: default safe deny"
            decision.confidence = 0.7
        
        self.pending_requests.pop(req_id, None)
        return decision

    def respond(self, req_id: str, approved: bool):
        future = self.pending_requests.get(req_id)
        if future and not future.done():
            if approved:
                future.set_result(True)
            else:
                future.set_result(False)