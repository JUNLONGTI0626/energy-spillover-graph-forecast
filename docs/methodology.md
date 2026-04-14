# Methodology

## 1. Overview

This project combines dynamic connectedness analysis and graph-based deep learning to study cross-market risk transmission in a six-variable daily energy system consisting of Electricity, Gas, WTI, Coal, Solar, and Wind.

The empirical methodology follows four linked stages.

First, the project estimates dynamic spillovers using the TVP-VAR-BK framework. This stage quantifies time-varying and frequency-dependent connectedness across the six energy variables.

Second, the project converts the resulting spillover outputs into a sequence of dynamic directed weighted graphs. In this representation, each market is a node, while pairwise spillovers define the cross-market transmission edges.

Third, the project constructs a forward-looking classification target, the High Spillover State (HSS), based on future values of the Total Connectedness Index (TCI).

Fourth, the project trains a topology-aware spatio-temporal graph transformer to predict future HSS from the evolving spillover network. Benchmark models are estimated in parallel to evaluate whether graph-based learning adds predictive value beyond conventional sequence models and statistical baselines.

The methodological objective is not only to describe the spillover structure of the energy system, but also to test whether that structure contains forward-looking information about future high-connectedness regimes.

---

## 2. Data representation and notation

Let the six-dimensional daily energy vector be denoted by:

\[
x_t = (x_{1t}, x_{2t}, x_{3t}, x_{4t}, x_{5t}, x_{6t})'
\]

where the elements correspond to:

- \(x_{1t}\): Electricity
- \(x_{2t}\): Gas
- \(x_{3t}\): WTI
- \(x_{4t}\): Coal
- \(x_{5t}\): Solar
- \(x_{6t}\): Wind

Depending on the empirical implementation, \(x_t\) may denote daily log returns or volatility-based series. The selected transformation must be stated explicitly in the corresponding experiment configuration.

All model inputs are organized in chronological order. Training, validation, and testing must preserve time order. No random reshuffling is allowed in forecasting tasks.

---

## 3. TVP-VAR-BK connectedness framework

### 3.1 Motivation

The six-variable energy system is expected to exhibit dynamic and heterogeneous spillover effects. These interactions are unlikely to remain constant over time and may differ across time horizons. A static full-sample connectedness measure would therefore mask both regime changes and frequency-specific risk transmission.

To address this, the project adopts the TVP-VAR-BK framework. This approach combines a time-varying parameter vector autoregression with frequency-domain connectedness decomposition. It allows the analysis to capture both evolving cross-market linkages and differences between short-, medium-, and long-run spillovers.

### 3.2 Time-varying VAR representation

The time-varying parameter VAR of order \(p\) is written as:

\[
x_t = \Phi_{1,t}x_{t-1} + \Phi_{2,t}x_{t-2} + \cdots + \Phi_{p,t}x_{t-p} + \varepsilon_t
\]

where:

- \(x_t\) is the \(6 \times 1\) vector of energy variables
- \(\Phi_{j,t}\) denotes time-varying coefficient matrices
- \(\varepsilon_t \sim (0, \Sigma_t)\) is the innovation process with time-varying covariance matrix \(\Sigma_t\)

The TVP-VAR structure allows both autoregressive coefficients and innovation covariances to evolve over time.

### 3.3 Generalized forecast error variance decomposition

From the time-varying VAR, the project derives the generalized forecast error variance decomposition (GFEVD). Let \(\theta_{ij,t}(H)\) denote the contribution of shocks in variable \(j\) to the \(H\)-step-ahead forecast error variance of variable \(i\) at time \(t\).

After normalization, the connectedness shares satisfy:

\[
\widetilde{\theta}_{ij,t}(H) = \frac{\theta_{ij,t}(H)}{\sum_{j=1}^{N}\theta_{ij,t}(H)}
\]

where \(N=6\) in the present application.

The normalized variance decomposition provides the basis for the spillover measures below.

### 3.4 Time-domain spillover measures

The Total Connectedness Index is defined as the share of forecast error variance attributable to cross-market shocks:

\[
TCI_t = \frac{1}{N} \sum_{i=1}^{N}\sum_{j=1, j \neq i}^{N}\widetilde{\theta}_{ij,t}(H) \times 100
\]

Directional spillovers transmitted **to** the system from market \(i\) are defined as:

\[
TO_{i,t} = \sum_{j=1, j \neq i}^{N}\widetilde{\theta}_{ji,t}(H)
\]

Directional spillovers received **from** the system by market \(i\) are defined as:

\[
FROM_{i,t} = \sum_{j=1, j \neq i}^{N}\widetilde{\theta}_{ij,t}(H)
\]

Net spillovers are then:

\[
NET_{i,t} = TO_{i,t} - FROM_{i,t}
\]

A positive \(NET_{i,t}\) implies that market \(i\) is a net transmitter of spillovers at time \(t\), while a negative value implies that market \(i\) is a net recipient.

### 3.5 Frequency-domain connectedness

To distinguish between different transmission horizons, the project applies the BK frequency decomposition to the time-varying variance decomposition.

This produces frequency-specific connectedness measures over pre-defined bands, such as:

- short-term connectedness
- medium-term connectedness
- long-term connectedness

The exact band definitions must be declared in the experiment configuration file and applied consistently across all runs.

Frequency-domain decomposition is important because the transmission of shocks in the energy system may be concentrated in short-run disturbances or may instead persist over longer horizons. The project therefore treats frequency heterogeneity as a core component of the empirical design rather than an optional extension.

### 3.6 Main outputs from the connectedness stage

The TVP-VAR-BK stage must generate at least the following outputs:

- daily \(TCI_t\)
- daily \(TO_{i,t}\)
- daily \(FROM_{i,t}\)
- daily \(NET_{i,t}\)
- pairwise spillover matrix for each time point
- frequency-specific connectedness outputs

These outputs serve both interpretive and predictive purposes. They are used in the empirical connectedness analysis and also form the basis for the dynamic graph representation used in the forecasting stage.

---

## 4. Dynamic spillover network construction

### 4.1 Motivation

The pairwise spillover structure can be naturally represented as a directed weighted graph. This allows the project to move from matrix-based connectedness measurement to network-aware forecasting.

Each time point \(t\) is associated with a graph snapshot:

\[
G_t = (V, E_t, W_t, X_t)
\]

where:

- \(V\) is the fixed set of six nodes
- \(E_t\) is the set of directed edges at time \(t\)
- \(W_t\) denotes edge weights derived from spillover intensities
- \(X_t\) denotes node features

### 4.2 Nodes

The node set is fixed across all graph snapshots:

\[
V = \{\text{Electricity}, \text{Gas}, \text{WTI}, \text{Coal}, \text{Solar}, \text{Wind}\}
\]

This fixed-node setting is advantageous because the graph evolves through edge weights and node states rather than through changes in node membership.

### 4.3 Edges

For each date \(t\), directed weighted edges are constructed from the non-diagonal entries of the pairwise spillover matrix. An edge from node \(j\) to node \(i\) reflects the magnitude of spillover transmitted from market \(j\) to market \(i\).

The baseline graph uses the total spillover matrix. Robustness extensions may alternatively use frequency-specific spillover matrices.

### 4.4 Node features

Each node at time \(t\) is associated with a feature vector. The baseline node feature set should include:

- own return or own volatility
- \(TO_{i,t}\)
- \(FROM_{i,t}\)
- \(NET_{i,t}\)

Additional node-level features may be included only if they are clearly documented and used consistently across experiments.

### 4.5 Temporal graph sequence

The sequence of graph snapshots \(\{G_t\}\) forms the core input to the graph forecasting model. Prediction is based on a rolling window of past graph snapshots:

\[
\mathcal{G}_{t-L+1:t} = \{G_{t-L+1}, \ldots, G_t\}
\]

where \(L\) is the lookback length chosen in the model configuration.

This rolling graph sequence allows the forecasting model to learn both structural dependencies across markets and their temporal evolution.

---

## 5. Forecast target construction

### 5.1 Objective

The project is designed to predict whether the energy system will enter a high-connectedness regime in the near future. The primary target is therefore a binary state variable rather than a continuous price or return series.

### 5.2 High Spillover State (HSS)

The primary forecast target is the High Spillover State:

\[
HSS_{t+1}=
\begin{cases}
1, & \text{if } TCI_{t+1} > c_q \\
0, & \text{otherwise}
\end{cases}
\]

where \(c_q\) is the threshold defined as the 75th percentile of the training-sample TCI distribution:

\[
c_q = Q_{0.75}(TCI_{train})
\]

Thus, the system is classified as being in a high spillover state when next-period total connectedness exceeds the training-sample high-risk threshold.

### 5.3 Rationale for the primary definition

The primary definition uses:

- one-step-ahead prediction
- a 75th percentile threshold
- a binary classification setup

This design is chosen because it matches the early warning objective. The model is not asked merely to fit the level of connectedness, but to identify whether the system is likely to move into a high-transmission regime in the next period.

### 5.4 Training-sample-only threshold rule

All thresholds must be computed from the training sample only. This rule is mandatory and is required to avoid look-ahead bias. Under no circumstances may the full sample be used to determine the classification threshold.

### 5.5 Robustness targets

Robustness definitions include three categories.

#### Alternative thresholds
The classification threshold may be redefined using:

- 80th percentile
- 90th percentile

#### Alternative horizons
The forecast horizon may be extended to:

- \(HSS_{t+3}\)
- \(HSS_{t+5}\)

#### Alternative state definitions
The target may also be defined using:

- average-window HSS, based on the future average TCI over a fixed horizon
- consecutive-day HSS, based on repeated threshold exceedance within a future window

The precise formulas for robustness targets are defined in the target-construction scripts and configs. The main paper, however, should treat \(HSS_{t+1}\) at the 75th percentile threshold as the baseline specification.

---

## 6. Topology-aware spatio-temporal graph transformer

### 6.1 Motivation

The forecasting object in this project is not a standard scalar or vector time series. It is a dynamic spillover network with evolving edge weights, node states, and cross-market topology. A forecasting model must therefore account for both:

- structural dependencies across nodes
- temporal dependencies across graph snapshots

A topology-aware spatio-temporal graph transformer is adopted as the main forecasting model because it is designed to learn from exactly this type of data structure.

### 6.2 Input structure

The model takes as input a rolling sequence of graph snapshots:

\[
\mathcal{G}_{t-L+1:t}
\]

where each graph includes:

- node identities
- node feature matrix
- directed weighted adjacency matrix

The output is the predicted probability that the system enters a high spillover state at the target horizon.

### 6.3 Why topology-aware modeling is necessary

A pure sequence model such as LSTM or GRU can process temporal information but does not explicitly exploit the spillover topology. By contrast, the topology-aware graph transformer can learn:

- which node-to-node transmission links matter most
- how spillover topology changes before high-connectedness episodes
- whether renewable and fossil energy nodes play asymmetric predictive roles

This feature is central to the research design because the predictive signal is assumed to lie in the evolving network structure rather than only in univariate persistence.

### 6.4 Primary forecasting task

The main model is trained for binary classification:

\[
\Pr(HSS_{t+1}=1 \mid \mathcal{G}_{t-L+1:t})
\]

The primary output is a probability score, which is then converted into a class prediction using an evaluation threshold set in the forecasting protocol.

### 6.5 Optional regression extension

As an auxiliary task, the project may also forecast continuous next-period connectedness:

\[
TCI_{t+1}
\]

This regression task is optional and secondary. The core research objective remains the classification of future high spillover states.

---

## 7. Benchmark models

Benchmark models are required to determine whether the graph-based forecasting architecture provides incremental predictive value.

### 7.1 Statistical baselines

Depending on the task, the project should include at least one conventional baseline such as:

- AR-based baseline
- logistic regression or probit classification baseline

These baselines provide a low-complexity reference.

### 7.2 Standard deep learning benchmarks

The project should also estimate standard sequence models:

- GRU
- LSTM
- TCN
- Transformer baseline

These models are important because they test whether the predictive gain comes specifically from dynamic graph modeling rather than from generic nonlinear sequence learning.

### 7.3 Principle of model comparison

The same forecast target, training protocol, and evaluation period must be used across all models. Any difference in performance should therefore be attributable to differences in model structure rather than to inconsistent data handling.

---

## 8. Forecast design and evaluation protocol

### 8.1 Time-ordered split

All forecasting experiments must preserve time order. A valid workflow includes:

- training period
- optional validation period
- out-of-sample test period

Random train-test splitting is not allowed.

### 8.2 Lookback window

The forecasting model uses a rolling historical window of length \(L\). The choice of \(L\) must be documented in the configuration file. Sensitivity analysis for alternative lookback lengths may be implemented as an extension.

### 8.3 Classification metrics

For the primary HSS classification task, the following metrics must be reported:

- Accuracy
- Precision
- Recall
- F1-score
- AUC

These metrics must be reported for both the primary model and all benchmark models.

### 8.4 Regression metrics

If continuous \(TCI_{t+1}\) forecasting is implemented, report:

- RMSE
- MAE
- \(R^2\)

### 8.5 Model comparison outputs

At minimum, the evaluation stage must generate:

- model comparison table
- ROC curve for the main classification task
- predicted-probability versus realized-state figure
- confusion matrix for the main model

---

## 9. Empirical interpretation strategy

The methodology is not purely predictive. It is designed to support interpretation at two levels.

First, the connectedness stage identifies how the six-variable energy system is linked in the time and frequency domains.

Second, the forecasting stage tests whether the evolving network structure anticipates future system stress.

Accordingly, empirical interpretation should focus on the following questions:

- which nodes are persistent net transmitters or receivers
- whether Solar and Wind differ in their connectedness roles
- whether high-connectedness states are preceded by identifiable network reconfiguration
- whether topology-aware graph learning improves predictive performance relative to non-graph baselines

---

## 10. Reproducibility requirements

The methodology must be implemented under the following reproducibility rules.

1. Raw source files must never be overwritten.
2. All paths must be relative.
3. Every major script must generate a short log in `outputs/logs/`.
4. Connectedness outputs, graph inputs, targets, and model outputs must be saved with explicit file names.
5. Thresholds for HSS must be estimated from training data only.
6. Primary and robustness specifications must be separated clearly.
7. No empirical result may be presented unless it is generated by the pipeline.

---

## 11. Primary methodological specification

The main empirical specification for this repository is:

- system: Electricity, Gas, WTI, Coal, Solar, Wind
- frequency: daily
- connectedness model: TVP-VAR-BK
- graph input: dynamic directed weighted spillover network
- node features: return or volatility, TO, FROM, NET
- main target: \(HSS_{t+1}\)
- threshold: training-sample 75th percentile of TCI
- main forecasting model: topology-aware spatio-temporal graph transformer
- benchmark models: AR/logit baseline, GRU, LSTM, TCN, Transformer baseline
- primary evaluation metrics: Accuracy, Precision, Recall, F1, AUC

This specification should be treated as the default reference point for all empirical development in the repository.

---

## 12. Extensions

Possible extensions may include:

- frequency-specific graph forecasting
- alternative node feature sets
- continuous TCI regression
- event-window forecasting around major energy shocks
- sub-sample analysis across crisis periods

These extensions are valuable but should be implemented only after the primary specification is fully reproducible and validated.
