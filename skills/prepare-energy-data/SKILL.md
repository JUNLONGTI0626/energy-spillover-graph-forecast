---
name: prepare-energy-data
description: Use this skill when the task is to clean, align, validate, and export daily data for Electricity, Gas, WTI, Coal, Solar, and Wind into a single modeling-ready dataset.
---

# Goal
Prepare a daily aligned dataset for the six-variable energy system.

# Inputs
- raw source files under `data/raw/`

# Outputs
- `data/interim/aligned_daily_prices.csv`
- `data/processed/daily_returns.csv`
- `outputs/logs/data_preparation_report.md`

# Required checks
- verify date parsing
- verify duplicate dates
- verify missing values by variable
- align market calendars
- do not modify raw files
