from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class VariableSpec:
    variable: str
    file_name: str
    source: str
    date_col: str
    value_col: str
    unified_col: str
    unit_meaning: str
    notes: str = "无"


VARIABLE_SPECS: List[VariableSpec] = [
    VariableSpec(
        variable="Electricity",
        file_name="eia_midc_daily_prices.xlsx",
        source="EIA Mid-C peak power daily prices",
        date_col="Trade date",
        value_col="Wtd avg price $/MWh",
        unified_col="Electricity",
        unit_meaning="Wtd avg price $/MWh（加权平均电价）",
    ),
    VariableSpec(
        variable="Gas",
        file_name="fred_henryhub_daily.csv",
        source="FRED (Henry Hub Natural Gas Spot Price, DHHNGSP)",
        date_col="observation_date",
        value_col="DHHNGSP",
        unified_col="Gas",
        unit_meaning="美元/MMBtu（现货）",
    ),
    VariableSpec(
        variable="WTI",
        file_name="fred_wti_daily.csv",
        source="FRED (WTI Crude Oil Spot Price, DCOILWTICO)",
        date_col="observation_date",
        value_col="DCOILWTICO",
        unified_col="WTI",
        unit_meaning="美元/桶（现货）",
    ),
    VariableSpec(
        variable="Coal",
        file_name="Newcastle Coal Futures Historical Data.csv",
        source="Newcastle Coal Futures Historical Data export",
        date_col="Date",
        value_col="Price",
        unified_col="Coal",
        unit_meaning="Price（通常为美元/吨）",
    ),
    VariableSpec(
        variable="Solar",
        file_name="tan_daily.csv.xlsx",
        source="TAN ETF daily historical export（文件内未显式来源）",
        date_col="Date",
        value_col="Close",
        unified_col="Solar",
        unit_meaning="ETF 收盘价（美元/份额）",
    ),
    VariableSpec(
        variable="Wind",
        file_name="fan_daily.xlsx",
        source="First Trust Global Wind Energy ETF (FAN) Price History export",
        date_col="Date",
        value_col="Market Price",
        unified_col="Wind",
        unit_meaning="ETF 市价（美元/份额）",
    ),
]


def _read_raw_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        try:
            return pd.read_excel(path)
        except ImportError as exc:
            raise ImportError(
                "Reading Excel files requires 'openpyxl'. Please install it and rerun."
            ) from exc
    raise ValueError(f"Unsupported file extension for {path.name}")


def _to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str).str.replace(",", "", regex=False).str.replace("%", "", regex=False),
        errors="coerce",
    )


def load_series(raw_dir: Path, spec: VariableSpec) -> pd.DataFrame:
    file_path = raw_dir / spec.file_name
    if not file_path.exists():
        raise FileNotFoundError(f"Missing raw file: {file_path}")

    table = _read_raw_table(file_path)
    required = {spec.date_col, spec.value_col}
    missing = required.difference(table.columns)
    if missing:
        raise KeyError(f"{spec.file_name} is missing columns: {sorted(missing)}")

    series = table[[spec.date_col, spec.value_col]].copy()
    series.columns = ["date", spec.unified_col]
    series["date"] = pd.to_datetime(series["date"], errors="coerce")
    series[spec.unified_col] = _to_numeric(series[spec.unified_col])
    series = series.dropna(subset=["date", spec.unified_col])
    series = series.sort_values("date")
    series = series.drop_duplicates(subset=["date"], keep="last")
    return series


def build_data_dictionary(dict_path: Path, stats: Dict[str, Dict[str, str]]) -> None:
    lines: List[str] = [
        "# Data Dictionary",
        "",
        "本文件由 `scripts/prepare_daily_data.py` 自动生成，用于记录六变量原始来源与标准化映射。",
        "",
        "| 变量 | 文件名 | 数据来源 | 样本区间 | 原始列名 | 统一后的列名 | 单位或价格含义 | 说明 |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for spec in VARIABLE_SPECS:
        date_range = stats[spec.variable]["sample_range"]
        raw_cols = f"`{spec.date_col}`, `{spec.value_col}`"
        lines.append(
            f"| {spec.variable} | `{spec.file_name}` | {spec.source} | {date_range} | {raw_cols} | `{spec.unified_col}` | {spec.unit_meaning} | {spec.notes} |"
        )

    dict_path.parent.mkdir(parents=True, exist_ok=True)
    dict_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_run_report(report_path: Path, aligned: pd.DataFrame, per_var_rows: Dict[str, int]) -> None:
    missing_counts = aligned.isna().sum().to_dict()
    date_start = aligned["date"].min().date().isoformat()
    date_end = aligned["date"].max().date().isoformat()

    lines = [
        "# Data Preparation Report",
        "",
        "- Script: `scripts/prepare_daily_data.py`",
        f"- Aligned sample: {date_start} ~ {date_end}",
        f"- Aligned rows: {len(aligned)}",
        "",
        "## Required checks",
        "- Date parsing: passed (invalid dates removed by `to_datetime(errors='coerce')`).",
        "- Duplicate dates: passed (deduplicated each series by date, keep last).",
        "- Missing values by variable after alignment:",
    ]
    lines.extend([f"  - {k}: {v}" for k, v in missing_counts.items() if k != "date"])
    lines.append("- Market calendar alignment: passed (inner join on date across all six variables).")
    lines.append("")
    lines.append("## Raw rows retained by variable")
    lines.extend([f"- {k}: {v}" for k, v in per_var_rows.items()])

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def prepare_daily_data(
    raw_dir: Path = Path("data/raw"),
    interim_output: Path = Path("data/interim/aligned_daily_prices.csv"),
    processed_output: Path = Path("data/processed/daily_returns.csv"),
    dictionary_output: Path = Path("docs/data_dictionary.md"),
    report_output: Path = Path("outputs/logs/data_preparation_report.md"),
) -> None:
    loaded = [load_series(raw_dir, spec) for spec in VARIABLE_SPECS]

    aligned = loaded[0]
    for frame in loaded[1:]:
        aligned = aligned.merge(frame, on="date", how="inner")

    aligned = aligned.sort_values("date").reset_index(drop=True)

    interim_output.parent.mkdir(parents=True, exist_ok=True)
    aligned.to_csv(interim_output, index=False)

    returns = aligned.copy()
    value_cols = [spec.unified_col for spec in VARIABLE_SPECS]
    returns[value_cols] = np.log(returns[value_cols]).diff()
    returns = returns.dropna().reset_index(drop=True)

    processed_output.parent.mkdir(parents=True, exist_ok=True)
    returns.to_csv(processed_output, index=False)

    stats = {}
    per_var_rows = {}
    for spec, frame in zip(VARIABLE_SPECS, loaded):
        stats[spec.variable] = {
            "sample_range": f"{frame['date'].min().date().isoformat()} ~ {frame['date'].max().date().isoformat()}"
        }
        per_var_rows[spec.variable] = len(frame)

    build_data_dictionary(dictionary_output, stats)
    build_run_report(report_output, aligned, per_var_rows)


if __name__ == "__main__":
    prepare_daily_data()
    print("Data preparation completed.")
