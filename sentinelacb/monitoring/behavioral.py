from __future__ import annotations
from collections import deque
from typing import Deque
from ..core.models import ActionEvent, RiskState, EnforcementDecision

class CircuitBreaker:
    def __init__(self, window_sec: float, limit: int):
        self.window_sec = window_sec
        self.limit = limit
        self.timestamps: Deque[float] = deque()

    def check_and_update(self, current_time: float) -> bool:
        self.timestamps.append(current_time)
        cutoff = current_time - self.window_sec
        while self.timestamps and self.timestamps[0] < cutoff:
            self.timestamps.popleft()
        return len(self.timestamps) > self.limit

class BehavioralMonitor:
    def __init__(self, window_sec: float, limit: int, alpha: float, deviation_penalty: float):
        self.circuit = CircuitBreaker(window_sec, limit)
        self.alpha = alpha
        self.deviation_penalty = deviation_penalty
        self.state = RiskState()

    def evaluate(self, event: ActionEvent, base_risk: float) -> EnforcementDecision:
        now = event.timestamp
        freq_exceeded = self.circuit.check_and_update(now)
        freq_penalty = self.deviation_penalty if freq_exceeded else 0.0
        
        self.state.temporal_risk = self.alpha * self.state.temporal_risk + (1 - self.alpha) * base_risk + freq_penalty
        self.state.temporal_risk = min(self.state.temporal_risk, 1.0)
        self.state.frequency_count = len(self.circuit.timestamps)
        self.state.deviation_score = freq_penalty
        self.state.last_updated = now

        if freq_exceeded:
            return EnforcementDecision(decision="DENY", risk_score=self.state.temporal_risk, confidence=0.9, reason="Circuit breaker tripped: rapid execution", layer_triggered="Layer3_Behavioral")
        return EnforcementDecision(decision="ALLOW", risk_score=self.state.temporal_risk, confidence=0.85, reason="Behavioral baseline normal", layer_triggered="Layer3_Behavioral")