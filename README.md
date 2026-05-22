# SentinelACB — Five-Layer Cybersecurity Framework for AI Control

This repository contains the prototype implementation and empirical validation code for the paper:

> M. Muttaka, "A Layered Cybersecurity Framework for Enforcing Human Control Over Autonomous AI Systems"

## Repository Structure

| File/Folder | Description |
|---|---|
| `advanced_agentic_ai_control_prototype_v2.py` | Original prototype — Table 3 layer-by-layer validation |
| `sentinelacb/` | Extended framework — 500-event adversarial simulation |
| `configs/experiment.yaml` | Experiment configuration (seed=42) |
| `outputs/metrics.csv` | Table 4 empirical results |
| `logs/audit_chain.jsonl` | Verified SHA-256 audit chain |

## Five Control Layers

| Layer | Name | Mechanism |
|---|---|---|
| 1 | Permission Boundaries | Allowlist P ⊆ A, high-risk set H ⊆ A |
| 2 | Human-in-the-Loop Gate | Interactive approval for a ∈ H |
| 3 | Circuit Breaker | Token bucket rate limiter |
| 4 | Kill Switch and Safe State | Hardware-isolated external control files |
| 5 | Audit Log | SHA-256 hash chain — tamper evident |

## Reproduce Table 3 — Layer-by-Layer Validation

```bash
python advanced_agentic_ai_control_prototype_v2.py

When prompted for HITL approval type yes and press Enter.

## Reproduce Table 4 — 500-Event Adversarial Simulation

python -m sentinelacb.cli.main --config configs/experiment.yaml

Results saved to outputs/metrics.csv

Author
Muhammad Muttaka
School of Cybersecurity, Astana IT University
Astana, Kazakhstan
255902@astanait.edu.kz
mmnasharifiya@gmail.com
License
MIT License
Citation
