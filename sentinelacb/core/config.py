from __future__ import annotations
import yaml
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class PermissionConfig(BaseModel):
    allowed_actions: List[str] = Field(default_factory=list)
    high_risk_actions: List[str] = Field(default_factory=list)
    denied_prefixes: List[str] = Field(default_factory=list)

class ThresholdConfig(BaseModel):
    risk_hitl: float = 0.65
    risk_block: float = 0.85
    risk_safe_state: float = 0.95
    frequency_window_sec: int = 10
    frequency_limit: int = 10

class ScoringConfig(BaseModel):
    weights: Dict[str, float] = Field(default={"sensitivity": 0.4, "criticality": 0.3, "context": 0.3})
    temporal_alpha: float = 0.3
    confidence_base: float = 0.5
    deviation_penalty: float = 0.15

class PoliciesConfig(BaseModel):
    permissions: PermissionConfig
    thresholds: ThresholdConfig
    scoring: ScoringConfig

class ExperimentConfig(BaseModel):
    name: str
    seed: int
    num_iterations: int
    deterministic: bool
    output_dir: str

class SimulationConfig(BaseModel):
    attack_distribution: Dict[str, float]

class EvaluationConfig(BaseModel):
    metrics: List[str]

class AppConfig(BaseModel):
    policies: PoliciesConfig
    experiment: ExperimentConfig
    simulation: SimulationConfig
    evaluation: EvaluationConfig

def _extract_section(data: Dict[str, Any], section_name: str) -> Dict[str, Any]:
    """Helper to extract nested config sections from YAML files."""
    if section_name in data and isinstance(data[section_name], dict):
        return data[section_name]
    return data

def load_policies(path: str = "configs/policies.yaml") -> PoliciesConfig:
    """Load policies configuration from YAML, handling nested 'policies:' key."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data = _extract_section(data, "policies")
    return PoliciesConfig.model_validate(data)

def load_experiment(path: str = "configs/experiment.yaml") -> ExperimentConfig:
    """Load experiment configuration from YAML, handling nested 'experiment:' key."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data = _extract_section(data, "experiment")
    return ExperimentConfig.model_validate(data)

def load_simulation(path: str = "configs/experiment.yaml") -> SimulationConfig:
    """Load simulation configuration from YAML, handling nested 'simulation:' key."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data = _extract_section(data, "simulation")
    return SimulationConfig.model_validate(data)

def load_evaluation(path: str = "configs/experiment.yaml") -> EvaluationConfig:
    """Load evaluation configuration from YAML, handling nested 'evaluation:' key."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data = _extract_section(data, "evaluation")
    return EvaluationConfig.model_validate(data)

def load_full_config(experiment_path: str = "configs/experiment.yaml", 
                     policies_path: str = "configs/policies.yaml") -> AppConfig:
    """Load complete application configuration from both YAML files."""
    return AppConfig(
        policies=load_policies(policies_path),
        experiment=load_experiment(experiment_path),
        simulation=load_simulation(experiment_path),
        evaluation=load_evaluation(experiment_path)
    )