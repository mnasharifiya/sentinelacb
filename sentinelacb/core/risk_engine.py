from __future__ import annotations
import math
from typing import Dict, Any
from ..core.models import ActionEvent

class RiskScoringEngine:
    """
    Mathematically grounded risk scoring engine.
    Formal Equation: R_t = α·R_{t-1} + (1-α)(w_s·S + w_c·C + w_k·K) + λ·F_p
    """
    def __init__(self, weights: Dict[str, float], alpha: float, confidence_base: float):
        self.weights = weights
        self.alpha = alpha
        self.confidence_base = confidence_base

    @staticmethod
    def normalize(val: float, low: float = 0.0, high: float = 1.0) -> float:
        return max(0.0, min(1.0, (val - low) / (high - low + 1e-9)))

    def compute_base_score(self, event: ActionEvent, context: Dict[str, Any]) -> Dict[str, float]:
        sensitivity = self.normalize(context.get("sensitivity", 0.5))
        criticality = self.normalize(context.get("criticality", 0.3))
        context_risk = self.normalize(context.get("context", 0.2))

        base_risk = (self.weights.get("sensitivity", 0.4) * sensitivity +
                     self.weights.get("criticality", 0.3) * criticality +
                     self.weights.get("context", 0.3) * context_risk)

        consistency = 1.0 - context.get("uncertainty", 0.3)
        confidence = 1.0 / (1.0 + math.exp(-5.0 * (consistency - self.confidence_base)))

        return {"base_risk": base_risk, "confidence": confidence}

    def apply_temporal_accumulation(self, prev_risk: float, base_risk: float, freq_penalty: float = 0.0) -> float:
        temporal_risk = self.alpha * prev_risk + (1 - self.alpha) * base_risk + (1 - self.alpha) * freq_penalty
        return min(temporal_risk, 1.0)