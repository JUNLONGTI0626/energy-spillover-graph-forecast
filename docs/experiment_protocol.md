# Experiment Protocol

## 1. Purpose

This document defines the experiment rules for the repository. Its purpose is to ensure that all empirical results are reproducible, comparable, and free from preventable design errors such as look-ahead bias, inconsistent target definitions, or uncontrolled output naming.

This protocol applies to all major experiment stages, including:

- data preparation
- TVP-VAR-BK estimation
- spillover graph construction
- HSS target construction
- model training
- benchmark comparison
- forecast evaluation
- robustness testing

All scripts and model runs must follow this protocol unless an exception is explicitly documented in the run log.

---

## 2. Core empirical objective

The main empirical objective is to test whether the dynamic spillover network of a six-variable daily energy system contains forward-looking information about future high-connectedness states.

The six variables are:

- Electricity
- Gas
- WTI
- Coal
- Solar
- Wind

The default pipeline is:

1. prepare daily aligned data
2. estimate TVP-VAR-BK connectedness
3. construct dynamic spillover graphs
4. define HSS targets
5. train the topology-aware spatio-temporal graph transformer
6. compare against benchmark models
7. export reproducible evaluation outputs

---

## 3. General principles

All experiments must satisfy the following principles.

### 3.1 Time order must be preserved
This is a forecasting project. Therefore, all splits must respect chronology. Random shuffling is not allowed in training, validation, or testing.

### 3.2 No look-ahead bias
No information from the future may enter:

- feature construction
- target construction
- threshold selection
- normalization fitted on training data
- model selection

Any procedure that uses future information must be rejected unless clearly separated as a descriptive exercise rather than a forecasting experiment.

### 3.3 Training sample is the only source for thresholds and fitted transforms
Any threshold used to define the target variable must be estimated from the training sample only. Any scaler, normalizer, or preprocessing transform that requires fitting must also be fitted on the training sample only.

### 3.4 Primary and robustness specifications must remain separate
The repository must clearly distinguish:

- main specification
- robustness specifications
- exploratory extensions

Main results must not be mixed with robustness outputs in file naming or reporting.

### 3.5 All outputs must be saved
Every major script must produce saved outputs, not only console output.

At minimum, each major stage must save:

- main result files
- a short run report
- clearly named outputs
- reproducible logs

---

## 4. Data protocol

## 4.1 Raw data handling

Raw data must be placed under:

- `data/raw/`

Rules:

1. raw files must never be overwritten
2. raw files must not be manually modified after placement in `data/raw/`
3. any cleaning or transformation must be done in downstream scripts
4. file provenance should be recorded whenever possible

### Minimum raw-data expectations
Each raw dataset should have at least:

- date column
- variable identifier or source identifier
- price or index value

If a source file uses nonstandard date formats or contains duplicate dates, this must be addressed in the data-preparation script and recorded in the run log.

---

## 4.2 Data alignment

All six variables must be aligned to a common daily calendar before modeling.

Rules:

1. date parsing must be explicit
2. duplicate dates must be checked
3. missing values must be reported by variable
4. alignment decisions must be documented
5. the final aligned file must preserve exact variable order

The fixed variable order for all downstream steps is:

1. Electricity
2. Gas
3. WTI
4. Coal
5. Solar
6. Wind

This order must remain unchanged across:

- prepared datasets
- TVP-VAR-BK inputs
- graph nodes
- benchmark model inputs
- output tables

### Output files
At minimum, the data-preparation stage must save:

- `data/interim/aligned_daily_prices.csv`
- `data/processed/daily_returns.csv` or the corresponding modeling-ready file
- `outputs/logs/data_preparation_report.md`

---

## 4.3 Variable transformation

The transformation used in modeling must be explicitly declared.

Possible transformations include:

- log prices for descriptive purposes
- daily log returns
- volatility-based series

The main transformation used in forecasting experiments must be documented in:

- `docs/data_dictionary.md`
- `configs/`
- the corresponding run log

If the project switches from return spillovers to volatility spillovers, this must be treated as a distinct specification rather than a silent substitution.

---

## 5. TVP-VAR-BK estimation protocol

## 5.1 Purpose

The TVP-VAR-BK stage is responsible for producing the dynamic connectedness structure that underlies both the empirical analysis and the forecasting system.

## 5.2 Required inputs

The connectedness script must read from the modeling-ready dataset, such as:

- `data/processed/daily_returns.csv`

and from a config file, such as:

- `configs/tvpvarbk.yaml`

## 5.3 Required outputs

At minimum, this stage must produce:

- `data/features/tci_daily.csv`
- `data/features/net_spillovers_daily.csv`
- `data/features/pairwise_spillovers_daily.csv`
- `data/features/frequency_connectedness_daily.csv`
- `outputs/logs/tvpvarbk_run_report.md`

## 5.4 Required checks

Every TVP-VAR-BK run must verify:

1. variable order
2. date continuity after alignment
3. lag order setting
4. forecast horizon setting
5. frequency-band settings
6. missing values in connectedness outputs
7. output dimensions

Any failed check must be written into the run log.

## 5.5 Naming rule for runs

Every connectedness run should use explicit naming that records the main settings.

Suggested naming format:

- `tvpvarbk_main_p1_h10`
- `tvpvarbk_main_p1_h20`
- `tvpvarbk_freq_s1`
- `tvpvarbk_freq_s2`

The exact naming convention can be refined, but each run name must encode the main parameter choices.

---

## 6. Spillover graph construction protocol

## 6.1 Purpose

The graph construction stage converts time-varying spillover outputs into dynamic directed weighted graphs suitable for graph-based forecasting.

## 6.2 Graph definition

### Nodes
The node set is fixed:

- Electricity
- Gas
- WTI
- Coal
- Solar
- Wind

### Edges
Edges are constructed from pairwise spillover values.

Rules:

1. only non-diagonal spillover values may define cross-node edges
2. direction must be preserved
3. edge weights must be saved numerically
4. graph snapshots must be aligned to the time index used in forecasting

## 6.3 Node features

The baseline node feature set should include:

- own return or volatility
- TO spillover
- FROM spillover
- NET spillover

Any expanded node feature set must be documented and versioned.

## 6.4 Required outputs

At minimum, the graph construction stage must save:

- `data/features/graph_edges.parquet`
- `data/features/graph_nodes.parquet`
- `data/features/graph_snapshots/`
- `outputs/logs/graph_construction_report.md`

## 6.5 Frequency-specific graph extensions

The baseline graph uses the total spillover matrix.

Frequency-specific graph variants may be constructed for robustness using:

- short-frequency spillover matrix
- medium-frequency spillover matrix
- long-frequency spillover matrix

These variants must be saved separately and must not overwrite the baseline graph files.

---

## 7. Forecast target protocol

## 7.1 Primary target

The primary target is:

- `HSS_t+1`

Definition:

\[
HSS_{t+1}=
\begin{cases}
1, & \text{if } TCI_{t+1} > Q_{0.75}(TCI_{train}) \\
0, & \text{otherwise}
\end{cases}
\]

This is the default target for all main forecasting experiments.

## 7.2 Mandatory target rules

1. the threshold must be computed from the training sample only
2. the threshold must not be recomputed using the test sample
3. the target horizon must be explicit in the file name
4. primary and robustness targets must be stored separately

## 7.3 Robustness targets

The robustness target file may include:

### Alternative thresholds
- `HSS_t1_q80`
- `HSS_t1_q90`

### Alternative horizons
- `HSS_t3_q75`
- `HSS_t5_q75`

### Alternative state constructions
- average-window HSS
- consecutive-day HSS

## 7.4 Required outputs

At minimum, this stage must save:

- `data/features/hss_primary.csv`
- `data/features/hss_robustness.csv`
- `outputs/logs/hss_definition_report.md`

---

## 8. Train-validation-test split protocol

## 8.1 Chronological split only

All splits must follow time order.

A valid default design is:

- training set: earliest segment
- validation set: middle segment
- test set: latest segment

The exact ratio may vary by experiment, but chronology must always be preserved.

## 8.2 Suggested split logic

A practical default is:

- 70% training
- 15% validation
- 15% test

If a different split is used, it must be stated in the run log.

## 8.3 Walk-forward option

For more rigorous evaluation, walk-forward or rolling-origin evaluation may be used.

If this is implemented, the protocol must specify:

- lookback length
- refit frequency
- window type: rolling or expanding
- metric aggregation rule

Walk-forward evaluation is desirable but is not required for the first reproducible baseline.

---

## 9. Model training protocol

## 9.1 Main model

The main forecasting model is:

- Topology-aware Spatio-Temporal Graph Transformer

The primary task is binary classification of `HSS_t+1`.

## 9.2 Benchmark models

The benchmark set should include:

- AR-based or logistic baseline
- GRU
- LSTM
- TCN
- Transformer baseline

These models must use the same target and comparable split definitions.

## 9.3 Hyperparameter handling

Rules:

1. main hyperparameters must be saved in config files or logs
2. the same search logic must be used consistently across comparable models
3. test-set performance must not drive repeated manual tuning without documentation

If tuning is performed, the validation set must be used for model selection.

## 9.4 Random seeds

Where randomness exists, random seeds should be fixed and recorded.

At minimum, the run log should record:

- model seed
- data split seed if applicable
- framework seed if applicable

## 9.5 Saved outputs

Every model run must save to its own subfolder under:

- `outputs/models/<run_name>/`

Each run should save:

- model configuration
- checkpoint or final weights
- training history
- predicted probabilities or predicted labels
- evaluation summary

---

## 10. Evaluation protocol

## 10.1 Primary metrics for classification

For `HSS` prediction, report at least:

- Accuracy
- Precision
- Recall
- F1-score
- AUC

These metrics must be reported for:

- the main model
- each benchmark model

## 10.2 Optional metrics for regression

If continuous `TCI_{t+1}` forecasting is implemented, report:

- RMSE
- MAE
- \(R^2\)

Regression outputs must be clearly labeled as auxiliary rather than primary.

## 10.3 Required evaluation outputs

At minimum, the evaluation stage must save:

- `outputs/tables/model_comparison.csv`
- `outputs/figures/roc_curve_main.png`
- `outputs/figures/predicted_vs_actual_hss.png`
- `outputs/logs/evaluation_report.md`

Optional outputs may include:

- confusion matrix plot
- precision-recall curve
- calibration plot
- rolling forecast performance plot

## 10.4 Model comparison rule

Model performance must be compared on the same out-of-sample period.

No model may be evaluated on a shorter or easier test subset unless this is explicitly labeled as a separate experiment.

---

## 11. Robustness protocol

Robustness experiments must be organized in a separate section of the pipeline and must not overwrite the main-specification outputs.

## 11.1 Threshold robustness
Run the main model and benchmarks using:

- 80th percentile threshold
- 90th percentile threshold

## 11.2 Horizon robustness
Repeat forecasting for:

- `t+3`
- `t+5`

## 11.3 Target-construction robustness
Repeat experiments using:

- average-window HSS
- consecutive-day HSS

## 11.4 Graph-input robustness
Repeat experiments using:

- total spillover graph
- frequency-specific graph inputs

## 11.5 Sample robustness
If data length permits, robustness may also include sub-sample tests, such as:

- pre-crisis period
- crisis period
- post-crisis period

Any sub-sample design must be explicitly documented.

---

## 12. Logging protocol

Every major script must write a short markdown log under:

- `outputs/logs/`

Each log should include:

1. script name
2. date and time of run
3. main input files
4. main output files
5. parameter settings
6. key checks performed
7. warnings or failures
8. summary of what was completed

### Minimum log files
The pipeline should at least generate:

- `data_preparation_report.md`
- `tvpvarbk_run_report.md`
- `graph_construction_report.md`
- `hss_definition_report.md`
- `model_training_report.md`
- `evaluation_report.md`

---

## 13. File naming protocol

File names must be explicit and reproducible.

### Good examples
- `tci_daily_main.csv`
- `net_spillovers_daily_main.csv`
- `graph_edges_total_main.parquet`
- `hss_t1_q75_primary.csv`
- `graph_transformer_hss_t1_q75_run01/`

### Avoid
- `final.csv`
- `new_results.csv`
- `test2.csv`
- `latest_model/`

File names should make it possible to infer:

- data type
- target definition
- model type
- main parameter choice
- whether the file belongs to the main spec or robustness

---

## 14. Main specification checklist

A main-specification experiment is valid only if all items below are satisfied.

### Data
- [ ] six variables aligned correctly
- [ ] no unresolved duplicate dates
- [ ] modeling-ready file saved

### Connectedness
- [ ] TVP-VAR-BK run completed
- [ ] TCI saved
- [ ] directional spillovers saved
- [ ] pairwise spillovers saved

### Graph
- [ ] graph nodes fixed as specified
- [ ] graph edges saved
- [ ] node features saved

### Target
- [ ] `HSS_t+1` created
- [ ] 75th percentile threshold computed from training sample only
- [ ] target file saved

### Model
- [ ] topology-aware spatio-temporal graph transformer trained
- [ ] benchmark models trained
- [ ] outputs saved in unique folders

### Evaluation
- [ ] out-of-sample metrics computed
- [ ] model comparison table saved
- [ ] main figures saved
- [ ] evaluation log written

Only experiments that satisfy this checklist should be treated as main results.

---

## 15. Recommended execution order

The recommended order of empirical implementation is:

1. data preparation
2. TVP-VAR-BK estimation
3. graph construction
4. HSS construction
5. baseline forecasting models
6. main graph-transformer model
7. evaluation and comparison
8. robustness experiments
9. paper-ready table and figure generation

This order should be followed unless a strong reason for deviation is recorded.

---

## 16. Scope rule

This repository is built for one specific empirical paper. Therefore:

- keep the pipeline tightly linked to the six-variable energy system
- do not generalize scripts prematurely into an abstract library
- prioritize reproducibility over architectural sophistication
- add complexity only when the main specification already runs end-to-end

The first goal is a complete working pipeline, not maximal engineering abstraction.

---

## 17. Final rule

No empirical claim should be written into the paper unless it is backed by files generated under this protocol.
