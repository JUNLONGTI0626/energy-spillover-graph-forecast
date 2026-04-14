# Project Overview

## Project title
Dynamic Spillover Networks and Early Warning of High-Connectedness States in Energy Markets

## Research objective
This project studies the dynamic spillover structure of a six-variable daily energy system and evaluates whether the evolving spillover network contains forward-looking information about future high-connectedness risk states.

The six variables are:

- Electricity
- Gas
- WTI
- Coal
- Solar
- Wind

The project combines connectedness modeling and deep learning in a unified framework. It first estimates dynamic time-frequency spillovers using TVP-VAR-BK, then converts spillover outputs into dynamic graph representations, and finally uses a topology-aware spatio-temporal graph transformer to predict future high spillover states.

## Core research questions
This repository is built to answer the following questions:

1. Do Electricity, Gas, WTI, Coal, Solar, and Wind exhibit significant time-varying and frequency-dependent spillovers?
2. How does the cross-market spillover network evolve over time, and how do the roles of traditional and renewable energy nodes change?
3. Does the dynamic spillover network contain predictive information about future high-connectedness states?
4. Can graph-based deep learning outperform standard time-series and benchmark models in forecasting future system stress?

## Main empirical workflow
The empirical workflow follows seven stages:

1. Prepare and align daily market data for the six-variable energy system.
2. Estimate dynamic connectedness using the TVP-VAR-BK framework.
3. Export spillover outputs, including TCI, directional spillovers, net spillovers, pairwise spillovers, and frequency-domain measures.
4. Convert spillover outputs into dynamic spillover graphs.
5. Construct the forecast target, namely the High Spillover State (HSS).
6. Train the topology-aware spatio-temporal graph transformer and benchmark models.
7. Evaluate predictive performance and generate paper-ready tables, figures, and logs.

## Variable system
The project uses the following six-node energy system:

- **Electricity**: terminal energy price and downstream market stress indicator
- **Gas**: natural gas market indicator
- **WTI**: crude oil market benchmark
- **Coal**: traditional high-carbon energy market indicator
- **Solar**: solar energy market indicator
- **Wind**: wind energy market indicator

The system is intentionally designed to capture interactions among terminal energy, fossil energy, and renewable energy markets.

## Connectedness framework
The project uses the TVP-VAR-BK framework to model dynamic spillovers.

The connectedness module should produce at least the following outputs:

- Total Connectedness Index (TCI)
- Directional spillovers TO and FROM
- Net spillovers
- Pairwise net spillovers
- Frequency-domain connectedness measures

These outputs are the bridge between the econometric spillover stage and the graph-based forecasting stage.

## Dynamic graph construction
The spillover system is converted into a sequence of dynamic directed weighted graphs.

### Nodes
The six variables are treated as graph nodes:

- Electricity
- Gas
- WTI
- Coal
- Solar
- Wind

### Edges
Directed weighted edges are constructed from pairwise spillover measures. Non-diagonal spillover values represent the intensity and direction of cross-market transmission.

### Node features
Each node may include a combination of the following features:

- return or volatility
- TO spillover
- FROM spillover
- NET spillover

The exact node feature set should be documented in model-specific scripts and config files.

## Forecast target
The primary forecast target is the **High Spillover State (HSS)**.

### Primary definition
The main target is defined as:

- `HSS_t+1 = 1` if `TCI_t+1` exceeds the 75th percentile threshold computed from the training sample
- `HSS_t+1 = 0` otherwise

This target is intended to capture whether the system enters a high-connectedness regime in the next period.

### Robustness definitions
Additional robustness targets should include:

- threshold at the 80th percentile
- threshold at the 90th percentile
- forecast horizon of `t+3`
- forecast horizon of `t+5`
- average-window HSS
- consecutive-day HSS

Thresholds must always be computed from the training sample only.

## Main model
The primary forecasting model is:

**Topology-aware Spatio-Temporal Graph Transformer**

This model is used because the research object is not a standard univariate or multivariate time series, but a dynamic spillover network with evolving topology and time dependence.

The model should use dynamic graph inputs derived from TVP-VAR-BK outputs to predict future HSS.

## Benchmark models
The following benchmark models should be maintained for comparison:

- AR-based or logistic baseline where appropriate
- GRU
- LSTM
- TCN
- Transformer baseline

Benchmark results are required for all main forecasting experiments.

## Evaluation metrics
### Classification task
For HSS prediction, report at least:

- Accuracy
- Precision
- Recall
- F1-score
- AUC

### Optional regression task
If continuous TCI forecasting is also implemented, report:

- RMSE
- MAE
- R-squared

## Output requirements
Every major stage of the workflow must generate clear, reproducible outputs.

### Required output folders
- `data/interim/`
- `data/processed/`
- `data/features/`
- `outputs/tables/`
- `outputs/figures/`
- `outputs/models/`
- `outputs/logs/`

### Minimum output expectations
- cleaned daily aligned dataset
- spillover output files
- graph input files
- HSS target files
- saved model outputs
- evaluation tables
- figures for connectedness and prediction
- run logs for each major script

## Reproducibility rules
This repository follows these rules:

1. Never overwrite raw source files.
2. Use relative paths only.
3. Save all major outputs with explicit names.
4. Write a short run report for each major script.
5. Keep the workflow deterministic whenever possible.
6. Do not fabricate results or fill missing outputs with placeholders presented as real findings.

## Scope of the repository
This repository is intended for empirical analysis, model training, evaluation, and paper-ready output generation for a six-variable daily energy spillover forecasting project.

It is not intended to serve as a general-purpose forecasting library. All development should remain tightly linked to the research design of this paper.

## Immediate setup priority
The first development priority is:

1. define the six variables and data sources
2. prepare the aligned daily dataset
3. implement TVP-VAR-BK outputs
4. construct graph-ready spillover data
5. define HSS targets
6. train and compare forecasting models

## Expected end product
The final deliverable of this repository is a complete and reproducible empirical pipeline that supports a paper on dynamic spillover networks and early warning of high-connectedness states in energy markets.
