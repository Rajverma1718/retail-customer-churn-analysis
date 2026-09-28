from pathlib import Path
import pandas as pd
import numpy as np

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

ROOT = Path(__file__).parent
SOURCE = ROOT / 'data' / 'raw' / 'Online Retail.xlsx'
OUT = ROOT / 'outputs'
OUT.mkdir(exist_ok=True)
CHURN_DAYS = 90

df = pd.read_excel(SOURCE)
df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
df = df.rename(columns={'invoicedate': 'invoice_date', 'unitprice': 'unit_price', 'customerid': 'customer_id', 'invoiceno': 'invoice_no'})
df['invoice_date'] = pd.to_datetime(df['invoice_date'], errors='coerce')
df['customer_id'] = pd.to_numeric(df['customer_id'], errors='coerce')
df = df.drop_duplicates()
df = df[df['customer_id'].notna() & df['invoice_date'].notna()]
df = df[~df['invoice_no'].astype(str).str.startswith('C')]
df = df[(df['quantity'] > 0) & (df['unit_price'] > 0)].copy()
df['revenue'] = df['quantity'] * df['unit_price']

analysis_date = df['invoice_date'].max()
orders = df.groupby(['customer_id', 'invoice_no', 'invoice_date', 'country'], as_index=False)['revenue'].sum()
customer = orders.groupby('customer_id').agg(
    last_purchase=('invoice_date', 'max'),
    first_purchase=('invoice_date', 'min'),
    frequency=('invoice_no', 'nunique'),
    total_spend=('revenue', 'sum'),
    average_order_value=('revenue', 'mean'),
    country=('country', 'first'),
).reset_index()
customer['recency_days'] = (analysis_date - customer['last_purchase']).dt.days
customer['customer_lifetime_days'] = (customer['last_purchase'] - customer['first_purchase']).dt.days
customer['churn_status'] = np.where(customer['recency_days'] > CHURN_DAYS, 'Churned', 'Active')
customer['frequency_band'] = pd.cut(customer['frequency'], bins=[0, 1, 3, 7, np.inf], labels=['1 order', '2-3 orders', '4-7 orders', '8+ orders'])
customer.to_csv(OUT / 'customer_metrics.csv', index=False)

country = customer.groupby('country', as_index=False).agg(
    customers=('customer_id', 'count'),
    churned_customers=('churn_status', lambda s: (s == 'Churned').sum()),
    average_spend=('total_spend', 'mean'),
)
country['churn_rate_pct'] = country['churned_customers'] / country['customers'] * 100
country = country[country['customers'] >= 20].sort_values('churn_rate_pct', ascending=False)
country.to_csv(OUT / 'churn_by_country.csv', index=False)

frequency = customer.groupby('frequency_band', observed=False).agg(
    customers=('customer_id', 'count'),
    churned_customers=('churn_status', lambda s: (s == 'Churned').sum()),
    average_spend=('total_spend', 'mean'),
).reset_index()
frequency['churn_rate_pct'] = frequency['churned_customers'] / frequency['customers'] * 100
frequency.to_csv(OUT / 'churn_by_frequency.csv', index=False)

print('TRANSACTION ROWS AFTER CLEANING:', len(df))
print('UNIQUE CUSTOMERS:', len(customer))
print('ANALYSIS DATE:', analysis_date.date())
print('CHURN THRESHOLD (DAYS):', CHURN_DAYS)
print('CHURNED CUSTOMERS:', int((customer['churn_status'] == 'Churned').sum()))
print('CHURN RATE (%):', round((customer['churn_status'] == 'Churned').mean() * 100, 2))
print('\nTOP COUNTRIES BY CHURN RATE - MINIMUM 20 CUSTOMERS')
print(country.head(10).to_string(index=False))
print('\nCHURN BY FREQUENCY')
print(frequency.to_string(index=False))

if plt is not None:
    top = country.head(10).sort_values('churn_rate_pct')
    top.plot.barh(x='country', y='churn_rate_pct', legend=False, title='Churn Rate by Country (20+ Customers)', figsize=(9, 5))
    plt.xlabel('Churn rate (%)')
    plt.tight_layout()
    plt.savefig(OUT / 'churn_rate_by_country.png', dpi=160)
    plt.close()

    customer.plot.scatter(x='recency_days', y='total_spend', c=customer['churn_status'].map({'Active': '#2a9d8f', 'Churned': '#e76f51'}), alpha=0.35, title='Customer Value vs. Recency', figsize=(8, 5))
    plt.xlabel('Days since last purchase')
    plt.ylabel('Total spend')
    plt.tight_layout()
    plt.savefig(OUT / 'customer_value_vs_recency.png', dpi=160)
    plt.close()
else:
    print('\nCharts skipped: install dependencies from requirements.txt to generate PNG visualizations.')
