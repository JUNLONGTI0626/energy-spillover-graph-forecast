---
name: run-tvpvarbk
description: Use this skill when the task is to estimate time-varying and frequency-domain spillovers for the six-variable energy system and export connectedness outputs.
---

# Goal
Estimate TVP-VAR-BK connectedness for the six-variable energy system.

# Inputs
- `data/processed/daily_returns.csv` or modeling-ready volatility file
- `configs/tvpvarbk.yaml`

# Outputs
- `data/features/tci_daily.csv`
- `data/features/net_spillovers_daily.csv`
- `data/features/pairwise_spillovers_daily.csv`
- `data/features/frequency_connectedness_daily.csv`
- `outputs/logs/tvpvarbk_run_report.md`

# Required checks
- validate variable order
- validate lag/horizon/frequency bands
- save all outputs with explicit names
