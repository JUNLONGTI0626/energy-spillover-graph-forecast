---
name: build-spillover-graph
description: Use this skill when the task is to convert TVP-VAR-BK outputs into dynamic graph data with node features and edge weights for graph forecasting models.
---

# Goal
Construct dynamic spillover graphs from connectedness outputs.

# Node set
Electricity, Gas, WTI, Coal, Solar, Wind

# Edge definition
Use non-diagonal pairwise spillover values as directed weighted edges.

# Node features
- return or volatility
- TO spillover
- FROM spillover
- NET spillover

# Outputs
- `data/features/graph_edges.parquet`
- `data/features/graph_nodes.parquet`
- `data/features/graph_snapshots/`
- `outputs/logs/graph_construction_report.md`
