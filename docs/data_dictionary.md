# Data Dictionary

本文件由 `scripts/prepare_daily_data.py` 自动生成，用于记录六变量原始来源与标准化映射。

| 变量 | 文件名 | 数据来源 | 样本区间 | 原始日期列 | 原始价格列 | 统一后列名 | 单位或价格含义 | 说明 |
|---|---|---|---|---|---|---|---|---|
| Electricity | `eia_midc_daily_prices.xlsx` | EIA Mid-C peak power daily prices | 2020-12-30 ~ 2025-12-23 | `Trade date` | `Wtd avg price $/MWh` | `Electricity` | Wtd avg price $/MWh（加权平均电价） | 无 |
| Gas | `fred_henryhub_daily.csv` | FRED (Henry Hub Natural Gas Spot Price, DHHNGSP) | 2021-01-04 ~ 2025-12-31 | `observation_date` | `DHHNGSP` | `Gas` | 美元/MMBtu（现货） | 无 |
| WTI | `fred_wti_daily.csv` | FRED (WTI Crude Oil Spot Price, DCOILWTICO) | 2021-01-04 ~ 2025-12-31 | `observation_date` | `DCOILWTICO` | `WTI` | 美元/桶（现货） | 无 |
| Coal | `Newcastle Coal Futures Historical Data.csv` | Newcastle Coal Futures Historical Data export | 2021-01-04 ~ 2025-12-31 | `Date` | `Price` | `Coal` | Price（通常为美元/吨） | 无 |
| Solar | `tan_daily.csv.xlsx` | TAN ETF daily historical export（文件内未显式来源） | 2021-01-04 ~ 2025-12-31 | `Date` | `Close` | `Solar` | ETF 收盘价（美元/份额） | 无 |
| Wind | `fan_daily.xlsx` | First Trust Global Wind Energy ETF (FAN) Price History export | 2021-01-04 ~ 2025-12-31 | `Date` | `Market Price` | `Wind` | ETF 市价（美元/份额） | 无 |
