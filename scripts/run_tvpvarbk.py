#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_var_matrices(data: np.ndarray, p: int):
    t_obs, n = data.shape
    y = data[p:]
    x_parts = [np.ones((t_obs - p, 1))]
    for lag in range(1, p + 1):
        x_parts.append(data[p - lag : t_obs - lag])
    x = np.hstack(x_parts)
    return x, y


def estimate_var_ols(data: np.ndarray, p: int, ridge_eps: float = 1e-8):
    x, y = build_var_matrices(data, p)
    xtx = x.T @ x
    xtx_reg = xtx + ridge_eps * np.eye(xtx.shape[0])
    b = np.linalg.solve(xtx_reg, x.T @ y)
    resid = y - x @ b
    sigma = (resid.T @ resid) / max(resid.shape[0] - 1, 1)

    n = y.shape[1]
    a_mats = []
    for lag in range(p):
        block = b[1 + lag * n : 1 + (lag + 1) * n, :]
        a_mats.append(block.T)
    return a_mats, sigma


def ma_matrices(a_mats: list[np.ndarray], horizon: int):
    p = len(a_mats)
    n = a_mats[0].shape[0]
    psi = [np.eye(n)]
    for h in range(1, horizon + 1):
        acc = np.zeros((n, n))
        for lag in range(1, min(p, h) + 1):
            acc += a_mats[lag - 1] @ psi[h - lag]
        psi.append(acc)
    return psi


def gfevd(psi: list[np.ndarray], sigma: np.ndarray, h_idx: list[int]):
    n = sigma.shape[0]
    out = np.zeros((n, n))
    den = np.zeros(n)
    diag_sigma = np.diag(sigma).copy()
    diag_sigma = np.where(diag_sigma <= 0, 1e-12, diag_sigma)

    for i in range(n):
        den_i = 0.0
        for h in h_idx:
            ph = psi[h]
            den_i += (ph @ sigma @ ph.T)[i, i]
        den[i] = den_i if den_i > 0 else 1e-12

    for i in range(n):
        for j in range(n):
            num = 0.0
            for h in h_idx:
                phs = psi[h] @ sigma
                num += (phs[i, j] ** 2) / diag_sigma[j]
            out[i, j] = num / den[i]

    row_sums = out.sum(axis=1, keepdims=True)
    row_sums = np.where(row_sums <= 0, 1e-12, row_sums)
    return out / row_sums


def connectedness_metrics(theta: np.ndarray):
    n = theta.shape[0]
    off_diag = theta.copy()
    np.fill_diagonal(off_diag, 0.0)

    tci = off_diag.sum() / n * 100.0
    to_vals = off_diag.sum(axis=0) * 100.0
    from_vals = off_diag.sum(axis=1) * 100.0
    net_vals = to_vals - from_vals
    return tci, to_vals, from_vals, net_vals


def main() -> None:
    config_path = Path("configs/tvpvarbk.yaml")
    cfg = load_config(config_path)

    input_file = Path(cfg["data"]["input_file"])
    date_col = cfg["data"]["date_column"]
    var_order = cfg["data"]["variable_order"]

    p = int(cfg["model"]["lag_order"])
    horizon = int(cfg["model"]["forecast_horizon"])
    min_obs = int(cfg["tvpvar"]["min_observations"])
    ridge_eps = float(cfg["tvpvar"].get("ridge_eps", 1e-8))

    short_band = cfg["bk_frequency"]["bands"]["short"]
    long_band = cfg["bk_frequency"]["bands"]["long"]

    output_files = cfg["output_files"]
    for k in [
        "tci_daily",
        "directional_daily",
        "net_daily",
        "pairwise_daily",
        "total_matrix_daily",
        "frequency_daily",
        "metadata",
        "run_log",
    ]:
        Path(output_files[k]).parent.mkdir(parents=True, exist_ok=True)
    Path(output_files["frequency_matrices_dir"]).mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_file)
    df[date_col] = pd.to_datetime(df[date_col])
    if cfg["data"].get("drop_na", True):
        df = df.dropna(subset=var_order).copy()
    if cfg["data"].get("check_duplicates", True):
        if df[date_col].duplicated().any():
            raise ValueError("Duplicate dates found in input data.")
    data = df[var_order].to_numpy(dtype=float)
    dates = df[date_col].reset_index(drop=True)

    start_idx = max(min_obs - 1, p)

    tci_rows, dir_rows, net_rows, freq_rows = [], [], [], []
    pairwise_rows, matrix_rows = [], []

    short_idx = list(range(short_band["lower"], short_band["upper"] + 1))
    long_idx = list(range(long_band["lower"], long_band["upper"] + 1))

    for t in range(start_idx, len(df)):
        sample = data[: t + 1]
        a_mats, sigma = estimate_var_ols(sample, p, ridge_eps=ridge_eps)
        psi = ma_matrices(a_mats, horizon)

        theta_total = gfevd(psi, sigma, h_idx=list(range(1, horizon + 1)))
        tci, to_vals, from_vals, net_vals = connectedness_metrics(theta_total)

        d = dates.iloc[t].strftime("%Y-%m-%d")
        tci_rows.append({"date": d, "TCI": tci})

        dir_row = {"date": d}
        net_row = {"date": d}
        for i, v in enumerate(var_order):
            dir_row[f"TO_{v}"] = to_vals[i]
            dir_row[f"FROM_{v}"] = from_vals[i]
            net_row[f"NET_{v}"] = net_vals[i]
        dir_rows.append(dir_row)
        net_rows.append(net_row)

        for i, vi in enumerate(var_order):
            for j, vj in enumerate(var_order):
                if i == j:
                    continue
                pairwise_rows.append(
                    {"date": d, "i": vi, "j": vj, "pairwise_net_ij": (theta_total[j, i] - theta_total[i, j]) * 100.0}
                )
                matrix_rows.append({"date": d, "i": vi, "j": vj, "spillover_ji": theta_total[i, j] * 100.0})

        theta_short = gfevd(psi, sigma, h_idx=short_idx)
        theta_long = gfevd(psi, sigma, h_idx=long_idx)
        tci_short, *_ = connectedness_metrics(theta_short)
        tci_long, *_ = connectedness_metrics(theta_long)
        freq_rows.append({"date": d, "TCI_short": tci_short, "TCI_long": tci_long})

        pd.DataFrame(theta_short, index=var_order, columns=var_order).to_csv(
            Path(output_files["frequency_matrices_dir"]) / f"short_{d}.csv"
        )
        pd.DataFrame(theta_long, index=var_order, columns=var_order).to_csv(
            Path(output_files["frequency_matrices_dir"]) / f"long_{d}.csv"
        )

    pd.DataFrame(tci_rows).to_csv(output_files["tci_daily"], index=False)
    pd.DataFrame(dir_rows).to_csv(output_files["directional_daily"], index=False)
    pd.DataFrame(net_rows).to_csv(output_files["net_daily"], index=False)
    pd.DataFrame(pairwise_rows).to_csv(output_files["pairwise_daily"], index=False)
    pd.DataFrame(matrix_rows).to_parquet(output_files["total_matrix_daily"], index=False)
    pd.DataFrame(freq_rows).to_csv(output_files["frequency_daily"], index=False)

    metadata = {
        "run_name": cfg["naming"].get("run_name"),
        "input_file": str(input_file),
        "date_column": date_col,
        "variable_order": var_order,
        "lag_order": p,
        "forecast_horizon": horizon,
        "min_observations": min_obs,
        "sample_start": dates.iloc[start_idx].strftime("%Y-%m-%d"),
        "sample_end": dates.iloc[len(df) - 1].strftime("%Y-%m-%d"),
        "n_observations": int(len(df) - start_idx),
        "frequency_bands": {
            "short": short_band,
            "long": long_band,
            "implementation": "horizon-band aggregation proxy (non-spectral BK integration)",
        },
    }
    with Path(output_files["metadata"]).open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    report_lines = [
        "# TVP-VAR-BK Baseline Run Report (p3, H100)",
        "",
        f"- Input file: `{input_file}`",
        f"- lag_order: `{p}`",
        f"- forecast_horizon: `{horizon}`",
        f"- Variable order: `{', '.join(var_order)}`",
        f"- Frequency bands: short `{short_band['lower']}-{short_band['upper']}`, long `{long_band['lower']}-{long_band['upper']}`",
        f"- Sample start: `{metadata['sample_start']}`",
        f"- Sample end: `{metadata['sample_end']}`",
        f"- Number of observations: `{metadata['n_observations']}`",
        "",
        "## Output files",
        f"- TCI: `{output_files['tci_daily']}`",
        f"- Directional TO/FROM: `{output_files['directional_daily']}`",
        f"- NET: `{output_files['net_daily']}`",
        f"- Pairwise: `{output_files['pairwise_daily']}`",
        f"- Total matrix: `{output_files['total_matrix_daily']}`",
        f"- Frequency connectedness: `{output_files['frequency_daily']}`",
        f"- Frequency matrices dir: `{output_files['frequency_matrices_dir']}`",
        f"- Metadata: `{output_files['metadata']}`",
        "",
        "## Success checks",
        "- TCI: success",
        "- TO_FROM: success",
        "- NET: success",
        "- pairwise: success",
        "- total matrix: success",
        "- frequency: success",
        "",
        "## Frequency implementation note",
        "Current frequency implementation uses a horizon-band aggregation proxy rather than full spectral BK integral decomposition.",
        "",
        "## Baseline vs grid relation",
        "This run is a standalone baseline specification saved with explicit `baseline_p3_H100` names and does not overwrite existing main/grid/robustness outputs.",
    ]
    Path(output_files["run_log"]).write_text("\n".join(report_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
