from __future__ import annotations
import numpy as np
from typing import List, Dict
from ..core.models import ActionEvent

class AdversarialSimulator:
    def __init__(self, seed: int = 42, distribution: Dict[str, float] = None):
        self.rng = np.random.RandomState(seed)
        self.distribution = distribution or {
            "unauthorized_permission": 0.25,
            "rapid_spamming": 0.20,
            "stealth_deviation": 0.25,
            "privilege_escalation": 0.30
        }
        self.categories = list(self.distribution.keys())
        self.probs = list(self.distribution.values())

    def generate_scenario(self, num_events: int) -> List[ActionEvent]:
        events = []
        categories = self.rng.choice(self.categories, size=num_events, p=self.probs)
        base_time = 1000000.0
        
        for i, cat in enumerate(categories):
            t = base_time + i * 0.005
            action_id = f"act_{i:04d}"
            
            if cat == "unauthorized_permission":
                events.append(ActionEvent(action_id=action_id, action_type="exfil_sensitive_data", parameters={"size_mb": 50}, timestamp=t))
            elif cat == "rapid_spamming":
                events.append(ActionEvent(action_id=action_id, action_type="read_sensor", parameters={}, timestamp=t))
            elif cat == "stealth_deviation":
                events.append(ActionEvent(action_id=action_id, action_type="execute_large_trade", parameters={"threshold_override": True}, timestamp=t))
            elif cat == "privilege_escalation":
                events.append(ActionEvent(action_id=action_id, action_type="modify_network_config", parameters={"firewall_rule": "ALLOW_ALL"}, timestamp=t))
        return events