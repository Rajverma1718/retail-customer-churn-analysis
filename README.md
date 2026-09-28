# Retail Customer Churn Analysis

An end-to-end customer retention analysis using real transaction data from the UCI Machine Learning Repository's Online Retail dataset. The data represents a UK-based, registered, non-store online retailer and covers transactions from 1 December 2010 to 9 December 2011.

## Business problem

Identify customers who became inactive, understand which customer groups are most at risk, and recommend practical retention actions.

## Churn definition

This project derives churn from transaction behavior because the source data does not contain a churn label. A customer is classified as **churned** when their last purchase is more than 90 days before the dataset's latest transaction date. The threshold is documented and can be changed in `analysis.py`.

## Tools

Python, Pandas, NumPy, Matplotlib, SQL, Excel-compatible CSV outputs

## Workflow

1. Load the original Excel workbook from UCI.
2. Remove cancellations, invalid quantities/prices, duplicate rows, and records without a customer ID.
3. Build customer-level RFM-style metrics: recency, frequency, monetary value, average order value, and country.
4. Classify customers as active or churned using the documented 90-day inactivity rule.
5. Compare churn rates by country, order frequency, and customer value.
6. Export clean customer metrics and charts for reporting or Power BI.

## Run locally

```bash
pip install -r requirements.txt
python analysis.py
```

## Outputs

- `outputs/customer_metrics.csv` - customer-level retention table
- `outputs/churn_by_country.csv` - country-level churn summary
- `outputs/churn_by_frequency.csv` - churn by purchase-frequency band
- `outputs/churn_rate_by_country.png` - visual analysis
- `outputs/customer_value_vs_recency.png` - visual analysis

## Data source

UCI Machine Learning Repository, Online Retail dataset:
https://archive.ics.uci.edu/dataset/352/online+retail

The original workbook is kept under `data/raw/` for reproducibility.
