# SentinelACB

**Research prototype and reproducibility artifacts for layered runtime security controls over autonomous AI systems.**

SentinelACB is the research prototype that preceded the development of the broader **AISec runtime-security framework**.

The repository contains the implementation and experimental artifacts associated with the study:

> **Layered Cybersecurity For Enforcing Human Control Over Autonomous AI**

Accepted at **IEEE SISY 2026**.

---

## Overview

Autonomous AI agents may propose actions that interact with external systems such as APIs, databases, files, or command-execution environments.

SentinelACB explores a layered security architecture in which agent-proposed actions are evaluated by externally enforced controls before consequential operations are permitted.

The prototype combines:

1. **Permission Boundaries**
2. **Human-in-the-Loop Review**
3. **Rate Limiting / Circuit Breaking**
4. **Kill-Switch and Safe-State Controls**
5. **Tamper-Evident Audit Logging**

The central design principle is that an AI agent's proposed action should not automatically be treated as authorization to execute that action.

---

## Repository Scope

This repository represents the **SentinelACB research prototype** used in the original layered-security study.

It is preserved for:

- research reproducibility;
- experimental verification;
- historical provenance;
- inspection of the original prototype architecture;
- reproduction of reported experimental tables.

SentinelACB should not be interpreted as the complete architecture or current development state of AISec.

For the actively developed runtime-security framework, see the main AISec repository.

---

## Repository Structure

| Path | Purpose |
|---|---|
| `advanced_agentic_ai_control_prototype_v2.py` | Original prototype used for layer-by-layer validation |
| `sentinelacb/` | Extended SentinelACB implementation used for adversarial simulation |
| `configs/experiment.yaml` | Reproducible experiment configuration |
| `outputs/metrics.csv` | Experimental metrics used in the reported evaluation |
| `logs/audit_chain.jsonl` | Tamper-evident SHA-256 audit-chain records |

---

## Security Architecture

### Layer 1 — Permission Boundaries

Actions are evaluated against explicitly defined permission boundaries.

Conceptually, for action space \(A\):

- \(P \subseteq A\) represents permitted actions;
- \(H \subseteq A\) represents actions requiring additional human authorization.

Actions outside the permitted boundary can be denied before execution.

---

### Layer 2 — Human-in-the-Loop Review

Selected high-risk actions can be deferred for human approval rather than being executed automatically.

Human review is intended for designated high-risk operations rather than every ordinary agent action.

---

### Layer 3 — Circuit Breaker

A token-bucket rate limiter constrains excessive or repeated action attempts.

This layer provides an additional operational control against uncontrolled action frequency.

---

### Layer 4 — Kill Switch and Safe State

The prototype includes externally controlled safe-state mechanisms that can restrict normal agent operation when containment is required.

This repository does **not** claim hardware-enforced isolation unless such isolation is independently provided by the deployment environment.

---

### Layer 5 — Tamper-Evident Audit Log

Security-relevant events are linked using SHA-256 hashes to provide tamper-evident audit records.

The audit mechanism is intended to make modification, deletion, or reordering detectable under the retained-chain assumptions.

It should not be interpreted as cryptographic immutability against complete host compromise or total replacement of the audit store.

---

## Reproducing the Experiments

### Layer-by-Layer Validation

Run:

```bash
python advanced_agentic_ai_control_prototype_v2.py
