---
name: train-topology-graph-transformer
description: Use this skill when the task is to train the topology-aware spatio-temporal graph transformer on dynamic spillover graphs to predict future HSS or TCI.
---

# Goal
Train the main graph forecasting model for HSS prediction.

# Primary task
Binary classification:
predict HSS_t+1 from dynamic spillover graph inputs.

# Benchmark tasks
- GRU
- LSTM
- TCN
- Transformer baseline
- Logit / AR baseline where appropriate

# Evaluation
- Accuracy
- Precision
- Recall
- F1
- AUC

# Outputs
- `outputs/models/<run_name>/`
- `outputs/tables/model_comparison.csv`
- `outputs/figures/roc_curve_main.png`
- `outputs/logs/model_training_report.md`
