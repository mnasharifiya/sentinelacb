```markdown
# SentinelACB — Five-Layer Cybersecurity Framework for AI Control

Prototype implementation and empirical validation code for:

> M. Muttaka, "A Layered Cybersecurity Framework for Enforcing Human Control Over Autonomous AI Systems"


## 📂 Repository Structure

| File/Folder | Description |
|-------------|-------------|
| `advanced_agentic_ai_control_prototype_v2.py` | Prototype implementation — reproduces Table 3 (layer-by-layer validation) |
| `sentinelacb/` | Extended framework — 500-event adversarial simulation |
| `configs/experiment.yaml` | Experiment configuration (seed = 42) |
| `outputs/metrics.csv` | Empirical results — reproduces Table 4 |
| `logs/audit_chain.jsonl` | Verified SHA-256 audit chain |


## 🛡️ Five Control Layers

| Layer | Name | Mechanism |
|-------|------|-----------|
| 1 | Permission Boundaries | Allowlist \(P \subseteq A\); high-risk set \(H \subseteq A\) |
| 2 | Human-in-the-Loop Gate | Interactive approval for \(a \in H\) |
| 3 | Circuit Breaker | Token bucket rate limiter |
| 4 | Kill Switch & Safe State | Hardware-isolated external control files |
| 5 | Audit Log | SHA-256 hash chain — tamper-evident |


## ▶️ Reproduce Table 3 — Layer-by-Layer Validation

Run the prototype script:

```bash
python advanced_agentic_ai_control_prototype_v2.py
```

When prompted for HITL approval, type `yes` and press Enter.


## ▶️ Reproduce Table 4 — 500-Event Adversarial Simulation

Run the adversarial simulation:

```bash
python -m sentinelacb.cli.main --config configs/experiment.yaml
```

Results are saved to `outputs/metrics.csv`.



## 🧪 Notes on Experiments

- **Seed**: The experiment configuration uses `seed = 42` for reproducibility.  
- **Metrics**: `outputs/metrics.csv` contains per-event metrics used to generate Table 4 in the paper.  
- **Audit chain**: `logs/audit_chain.jsonl` contains the SHA-256 hash chain entries; each line is a JSON object with event metadata and the corresponding hash.


## 👤 Author

**Muhammad Muttaka**  
School of Cybersecurity, Astana IT University  
Astana, Kazakhstan

📧 255902@astanait.edu.kz  
📧 mmnasharifiya@gmail.com


## 📜 License

MIT License
```
