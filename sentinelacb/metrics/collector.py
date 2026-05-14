from __future__ import annotations
import pandas as pd
from typing import List, Dict, Any
from ..core.models import EnforcementDecision, ActionEvent

class MetricsCollector:
    def __init__(self):
        self.results: List[Dict[str, Any]] = []

    def record(self, event: ActionEvent, decision: EnforcementDecision, ground_truth_action: str):
        is_malicious = ground_truth_action not in ["read_sensor", "minor_trade", "log_status"]
        detected = decision.decision in ["DENY", "HITL_PENDING", "SAFE_STATE_TRIGGER"]
        
        tp = int(is_malicious and detected)
        fp = int(not is_malicious and detected)
        fn = int(is_malicious and not detected)
        tn = int(not is_malicious and not detected)
        
        self.results.append({
            "action_id": event.action_id, "action_type": event.action_type,
            "decision": decision.decision, "risk_score": decision.risk_score,
            "latency_us": decision.latency_us, "tp": tp, "fp": fp, "fn": fn, "tn": tn
        })

    def compute_metrics(self) -> pd.DataFrame:
        df = pd.DataFrame(self.results)
        if df.empty: return pd.DataFrame()
        tp, fp, fn, tn = df["tp"].sum(), df["fp"].sum(), df["fn"].sum(), df["tn"].sum()
        return pd.DataFrame([{
            "detection_rate": tp / max(1, tp + fn),
            "false_positive_rate": fp / max(1, fp + tn),
            "false_negative_rate": fn / max(1, tp + fn),
            "enforcement_success_rate": tp / max(1, tp + fn),
            "mean_latency_us": df["latency_us"].mean(),
            "p99_latency_us": df["latency_us"].quantile(0.99),
            "total_events": len(df), "tp": tp, "fp": fp, "fn": fn, "tn": tn
        }])