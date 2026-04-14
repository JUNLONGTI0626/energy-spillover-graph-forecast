# AGENTS.md

## Repo purpose
This repository studies dynamic spillovers and early warning of high-connectedness states
in a six-variable energy system:
Electricity, Gas, WTI, Coal, Solar, and Wind.

Main workflow:
1. prepare daily market data
2. estimate TVP-VAR-BK spillover structure
3. construct dynamic spillover networks
4. define high spillover state targets (HSS)
5. train topology-aware spatio-temporal graph forecasting models
6. evaluate against benchmark models
7. produce paper-ready tables, figures, and writeups

## Source of truth
Read these before major edits:
- `docs/project_overview.md`
- `docs/methodology.md`
- `docs/experiment_protocol.md`
- `docs/result_writing_guide.md`

## Directory map
- `data/raw`: raw downloaded or manually collected source files
- `data/interim`: aligned and cleaned intermediate files
- `data/processed`: final modeling-ready panel files
- `data/features`: spillover, graph, and forecast feature datasets
- `scripts/`: runnable experiment entry points
- `src/`: reusable library code
- `outputs/tables`: csv/xlsx tables
- `outputs/figures`: paper figures
- `outputs/models`: saved checkpoints
- `outputs/logs`: run reports and experiment notes
- `skills/`: Codex skills for repeated workflows

## Working rules
- Never overwrite raw data.
- Prefer deterministic scripts over notebook-only logic.
- Every major script must save a run log under `outputs/logs/`.
- Every model run must write outputs to a uniquely named subfolder.
- Do not hardcode local absolute paths.
- Use config files in `configs/` whenever possible.
- When editing methodology-sensitive code, check `docs/methodology.md` first.
- When writing empirical text, follow Energy Economics style in `docs/result_writing_guide.md`.

## Forecast target
Primary target:
- `HSS_t+1`: whether next-period TCI exceeds the 75th percentile threshold computed from the training sample

Robustness targets:
- alternative thresholds: 80th and 90th percentile
- alternative horizons: t+3 and t+5
- alternative state definitions: average-window HSS and consecutive-day HSS

## Done criteria
A task is done only if:
1. code runs end-to-end
2. output files are saved to expected folders
3. a short log/report is written
4. file names are clear and reproducible
5. no raw data are modified
