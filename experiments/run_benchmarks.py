#!/usr/bin/env python3
"""Automated benchmark runner for IEEE-style reproducibility."""
import subprocess
import sys
import time
from pathlib import Path

def run_benchmark(config: str = "configs/experiment.yaml"):
    print(f"[BENCHMARK] Starting deterministic run: {config}")
    start = time.time()
    result = subprocess.run([sys.executable, "-m", "sentinelacb.cli.main", "--config", config], cwd=str(Path(__file__).parent.parent))
    elapsed = time.time() - start
    print(f"[BENCHMARK] Completed in {elapsed:.2f}s | Exit Code: {result.returncode}")
    return result.returncode == 0

if __name__ == "__main__":
    success = run_benchmark()
    sys.exit(0 if success else 1)