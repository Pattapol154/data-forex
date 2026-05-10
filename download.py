"""
download.py — Download tick data from Exness

Usage:
  python download.py           -> download all pairs
  python download.py EURUSD    -> download EURUSD only

Output: data/csv/{symbol}_Raw_Spread/{symbol}_Raw_Spread_{YYYY}_{MM}.csv
"""

import sys
import zipfile
from datetime import date
from pathlib import Path
from urllib.request import urlretrieve

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# ------------------- config -------------------

PAIRS   = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "GBPJPY",
           "AUDUSD", "USDCAD", "USDCHF", "EURJPY", "EURGBP"]
VARIANT = "Raw_Spread"
START   = (2022, 1)

_today  = date.today()
END     = (_today.year, _today.month - 1) if _today.month > 1 else (_today.year - 1, 12)

OUT_DIR = Path("data/csv")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ------------------- helpers -------------------

def month_range(start, end):
    """Yield (year, month) for every month from start to end."""
    year, month = start
    while (year, month) <= end:
        yield year, month
        month = month % 12 + 1
        if month == 1:
            year += 1

# ------------------- main ----------------------

def download_pair(pair: str):
    symbol  = f"{pair}_{VARIANT}"
    out_dir = OUT_DIR / symbol
    out_dir.mkdir(exist_ok=True)

    done = {f.stem[-7:] for f in out_dir.glob(f"{symbol}_[0-9]*.csv")}

    for year, month in month_range(START, END):
        tag = f"{year}_{month:02d}"
        if tag in done:
            continue

        url      = f"https://ticks.ex2archive.com/ticks/{symbol}/{year}/{month:02d}/Exness_{symbol}_{year}_{month:02d}.zip"
        tmp_file = Path(f"_tmp_{symbol}_{tag}.zip")

        print(f"  {year}-{month:02d} ...", end=" ", flush=True)
        try:
            urlretrieve(url, tmp_file)

            with zipfile.ZipFile(tmp_file) as zf, zf.open(zf.namelist()[0]) as f:
                df = pd.read_csv(f, usecols=["Timestamp", "Bid", "Ask", "Symbol"])

            df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="mixed", utc=True)
            df["Spread"]    = (df["Ask"] - df["Bid"]).round(5)
            df.to_csv(out_dir / f"{symbol}_{tag}.csv", index=False)
            print(f"{len(df):,} ticks")

        except Exception as e:
            print(f"error: {e}")
        finally:
            if tmp_file.exists():
                tmp_file.unlink()

    print(f"  [{symbol}] done")


if __name__ == "__main__":
    targets = sys.argv[1:] or PAIRS
    for pair in targets:
        print(f"\n=== {pair.upper()} ===")
        download_pair(pair.upper())
