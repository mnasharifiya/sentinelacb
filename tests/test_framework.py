import pytest
import asyncio
from sentinelacb.core.models import ActionEvent
from sentinelacb.policies.permissions import PermissionEngine
from sentinelacb.monitoring.behavioral import BehavioralMonitor
from sentinelacb.logging.audit import AuditChain
from sentinelacb.core.risk_engine import RiskScoringEngine
from sentinelacb.approval.hitl_gate import HITLGateway
from sentinelacb.enforcement.safestate import SafeStateController
from sentinelacb.api.middleware import EnforcementMiddleware

@pytest.fixture
def permissions():
    return PermissionEngine({"read_sensor", "minor_trade"}, {"execute_large_trade"}, ["shell_"])

@pytest.fixture
def monitor():
    return BehavioralMonitor(10, 10, 0.3, 0.15)

@pytest.fixture
def middleware(permissions, monitor):
    hitl = HITLGateway(timeout_sec=0.1)
    safe = SafeStateController()
    audit = AuditChain("logs/test_audit.jsonl")
    risk = RiskScoringEngine({"sensitivity":0.4, "criticality":0.3, "context":0.3}, 0.3, 0.5)
    return EnforcementMiddleware(permissions, monitor, hitl, safe, audit, risk)

def test_permission_deny(permissions):
    dec = permissions.evaluate(ActionEvent(action_id="1", action_type="shell_exec", parameters={}, timestamp=1.0))
    assert dec.decision == "DENY"

def test_audit_chain_integrity():
    audit = AuditChain("logs/test_chain_verify.jsonl")
    audit.append("a1", "ALLOW", 0.1)
    audit.append("a2", "DENY", 0.9)
    assert audit.verify() is True

@pytest.mark.asyncio
async def test_full_pipeline(middleware):
    evt = ActionEvent(action_id="3", action_type="read_sensor", parameters={}, timestamp=1.0)
    dec = await middleware.process_action(evt)
    assert dec.decision == "ALLOW"
    assert dec.latency_us > 0