import os
import sys
import argparse
from dataclasses import dataclass
from typing import Optional
import pandas as pd
import numpy as np
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    symbol: str = os.getenv("SYMBOL", "BTCUSDT")
    timeframe: str = os.getenv("TIMEFRAME", "15m")
    risk_pct: float = float(os.getenv("RISK_PCT", "1.0"))

def ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False).mean()

def generate_signals(df: pd.DataFrame, fast:int=20, slow:int=50):
    df = df.copy()
    df["ema_fast"] = ema(df["close"], fast)
    df["ema_slow"] = ema(df["close"], slow)
    df["buy"]  = (df["ema_fast"] > df["ema_slow"]) & (df["ema_fast"].shift(1) <= df["ema_slow"].shift(1))
    df["sell"] = (df["ema_fast"] < df["ema_slow"]) & (df["ema_fast"].shift(1) >= df["ema_slow"].shift(1))
    return df

def simulate(csv_path: str, fast:int=20, slow:int=50, head:int=20):
    df = pd.read_csv(csv_path)
    needed = {"open","high","low","close"}
    if not needed.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {sorted(needed)}")
    out = generate_signals(df, fast, slow)
    print(out.tail(head)[["close","ema_fast","ema_slow","buy","sell"]])

def main(argv=None):
    argv = argv or sys.argv[1:]
    p = argparse.ArgumentParser(description="DanAI example crypto bot (educational).")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_sim = sub.add_parser("simulate", help="Simulate EMA cross signals on CSV OHLCV data.")
    p_sim.add_argument("--csv", default="data.csv", help="Path to CSV with columns: open,high,low,close")
    p_sim.add_argument("--fast", type=int, default=20)
    p_sim.add_argument("--slow", type=int, default=50)
    p_sim.add_argument("--tail", type=int, default=20)

    args = p.parse_args(argv)
    if args.cmd == "simulate":
        simulate(args.csv, args.fast, args.slow, args.tail)

if __name__ == "__main__":
    main()