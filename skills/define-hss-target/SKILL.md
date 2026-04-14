---
name: define-hss-target
description: Use this skill when the task is to define and export the high spillover state target (HSS) for classification forecasting.
---

# Goal
Create the primary and robustness HSS targets.

# Primary target
HSS_t+1 = 1 if TCI_t+1 exceeds the 75th percentile threshold computed from the training sample.

# Robustness targets
- 80th percentile threshold
- 90th percentile threshold
- t+3 horizon
- t+5 horizon
- average-window HSS
- consecutive-day HSS

# Outputs
- `data/features/hss_primary.csv`
- `data/features/hss_robustness.csv`
- `outputs/logs/hss_definition_report.md`

# Rules
- threshold must be computed from training data only
- preserve exact horizon naming
