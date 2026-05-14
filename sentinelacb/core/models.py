from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator

class ActionEvent(BaseModel):
    action_id: str
    action_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float
    source_agent: str = "sim_agent_v1"

class EnforcementDecision(BaseModel):
    decision: Literal["ALLOW", "DENY", "HITL_PENDING", "SAFE_STATE_TRIGGER"]
    risk_score: float
    confidence: float
    reason: str
    latency_us: int = 0
    layer_triggered: str = "middleware"

class RiskState(BaseModel):
    temporal_risk: float = 0.0
    frequency_count: int = 0
    deviation_score: float = 0.0
    last_updated: float = 0.0

class AuditEntry(BaseModel):
    sequence: int
    action_id: str
    decision: str
    risk_score: float
    timestamp: float
    prev_hash: str
    payload_hash: str
    signature_hash: str

    @classmethod
    def create(cls, sequence: int, action_id: str, decision: str, risk_score: float, prev_hash: str) -> AuditEntry:
        payload_str = f"{sequence}|{action_id}|{decision}|{risk_score}"
        payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
        sig_input = f"{prev_hash}|{payload_hash}"
        signature_hash = hashlib.sha256(sig_input.encode("utf-8")).hexdigest()
        return cls(
            sequence=sequence,
            action_id=action_id,
            decision=decision,
            risk_score=risk_score,
            timestamp=datetime.now(timezone.utc).timestamp(),
            prev_hash=prev_hash,
            payload_hash=payload_hash,
            signature_hash=signature_hash
        )