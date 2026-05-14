import asyncio
import click
import time
import structlog
from pathlib import Path
from ..core.config import load_policies, load_experiment
from ..core.models import ActionEvent
from ..policies.permissions import PermissionEngine
from ..monitoring.behavioral import BehavioralMonitor
from ..approval.hitl_gate import HITLGateway
from ..enforcement.safestate import SafeStateController
from ..logging.audit import AuditChain
from ..core.risk_engine import RiskScoringEngine
from ..api.middleware import EnforcementMiddleware
from ..simulation.adversarial import AdversarialSimulator
from ..metrics.collector import MetricsCollector

logger = structlog.get_logger()

async def run_experiment(config_path: str):
    exp_cfg = load_experiment(config_path)
    pol_cfg = load_policies("configs/policies.yaml")
    logger.info("Initializing SentinelACB Framework", config=config_path, seed=exp_cfg.seed)

    permissions = PermissionEngine(set(pol_cfg.permissions.allowed_actions), set(pol_cfg.permissions.high_risk_actions), pol_cfg.permissions.denied_prefixes)
    monitor = BehavioralMonitor(pol_cfg.thresholds.frequency_window_sec, pol_cfg.thresholds.frequency_limit, pol_cfg.scoring.temporal_alpha, pol_cfg.scoring.deviation_penalty)
    hitl = HITLGateway()
    safe_state = SafeStateController()
    audit = AuditChain("logs/audit_chain.jsonl")
    risk_engine = RiskScoringEngine(pol_cfg.scoring.weights, pol_cfg.scoring.temporal_alpha, pol_cfg.scoring.confidence_base)
    
    middleware = EnforcementMiddleware(permissions, monitor, hitl, safe_state, audit, risk_engine)
    simulator = AdversarialSimulator(seed=exp_cfg.seed, distribution=None) # Uses default adversarial distribution
    collector = MetricsCollector()

    events = simulator.generate_scenario(exp_cfg.num_iterations)
    logger.info(f"Generated {len(events)} deterministic adversarial events")

    start = time.perf_counter()
    for evt in events:
        context = {
            "sensitivity": 0.8 if any(x in evt.action_type for x in ["trade", "exfil", "network"]) else 0.2,
            "criticality": 0.9 if any(x in evt.action_type for x in ["network", "power", "grid"]) else 0.3,
            "context": 0.6 if "escalation" in str(evt.parameters) else 0.2,
            "uncertainty": 0.2
        }
        
        # Simulate HITL auto-response for benchmarking (80% approve, 20% reject, 0.5s delay)
        if evt.action_type in pol_cfg.permissions.high_risk_actions:
            import random
            asyncio.get_running_loop().call_later(0.0005, hitl.respond, f"{evt.source_agent}:{evt.action_id}", random.random() > 0.2)

        decision = await middleware.process_action(evt, context)
        collector.record(evt, decision, evt.action_type)

    runtime = time.perf_counter() - start
    metrics_df = collector.compute_metrics()
    metrics_df["runtime_sec"] = runtime
    metrics_df["audit_integrity"] = float(audit.verify())
    
    Path("outputs").mkdir(exist_ok=True)
    metrics_df.to_csv("outputs/metrics.csv", index=False)
    logger.info("Experiment complete", metrics=metrics_df.to_dict(orient="records"))
    logger.info("Audit Chain Verification", valid=audit.verify())

@click.command()
@click.option("--config", default="configs/experiment.yaml", help="Path to experiment config")
def main(config: str):
    asyncio.run(run_experiment(config))

if __name__ == "__main__":
    main()