import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# ------------------- config -------------------

PAIRS   = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "GBPJPY",
           "AUDUSD", "USDCAD", "USDCHF", "EURJPY", "EURGBP"]
VARIANT = "Raw_Spread"
IN_DIR  = Path("data/csv")
OUT_DIR = Path("data/mt5_ticks")

# ------------------- helpers -------------------

def to_mt5(df: pd.DataFrame) -> pd.DataFrame:
    """Convert a tick DataFrame to MT5 import format."""
    df = df.sort_values("Timestamp")
    ms = (df["Timestamp"].dt.microsecond // 1000).map("{:03d}".format)
    return pd.DataFrame({
        "Date":   df["Timestamp"].dt.strftime("%Y.%m.%d"),
        "Time":   df["Timestamp"].dt.strftime("%H:%M:%S.") + ms,
        "Bid":    df["Bid"],
        "Ask":    df["Ask"],
        "Last":   0,
        "Volume": 0,
        "Flags":  6,
    })

# ------------------- main ----------------------

def convert_pair(pair: str):
    symbol   = f"{pair}_{VARIANT}"
    src_dir  = IN_DIR  / symbol
    dest_dir = OUT_DIR / symbol
    dest_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(src_dir.glob(f"{symbol}_[0-9]*.csv"))
    if not files:
        print(f"  [{symbol}] no files found — run download.py first")
        return

    for src in files:
        dest = dest_dir / src.name
        if dest.exists():
            print(f"  [skip] {src.name}")
            continue

        df = pd.read_csv(src)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="mixed", utc=True)
        to_mt5(df).to_csv(dest, index=False, header=False)
        print(f"  [save] {src.name}  ({len(df):,} ticks)")

    print(f"  [{symbol}] done")


if __name__ == "__main__":
    targets = sys.argv[1:] or PAIRS
    for pair in targets:
        print(f"\n=== {pair.upper()} ===")
        convert_pair(pair.upper())
