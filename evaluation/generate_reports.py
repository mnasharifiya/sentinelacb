import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def generate():
    metrics_path = Path("outputs/metrics.csv")
    if not metrics_path.exists():
        print("❌ Run experiment first: python -m sentinelacb.cli.main")
        return

    df = pd.read_csv(metrics_path)
    print("\n📊 SENTINELACB EVALUATION REPORT")
    print("="*40)
    for col in df.columns:
        if col not in ["tp", "fp", "fn", "tn"]:
            print(f"{col:<25}: {df[col].iloc[0]:.4f}")
    
    Path("outputs").mkdir(exist_ok=True)
    plt.figure(figsize=(7, 4))
    plt.hist(df["latency_us"] if "latency_us" in df else [0], bins=50, edgecolor="black", alpha=0.7, color="#1f77b4")
    plt.title("Enforcement Latency Distribution (μs)")
    plt.xlabel("Latency (microseconds)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig("outputs/latency_distribution.png", dpi=300)
    print("\n📈 Saved outputs/latency_distribution.png")

if __name__ == "__main__":
    generate()