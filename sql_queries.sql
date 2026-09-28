-- Load outputs/customer_metrics.csv into a table named customer_metrics.

-- 1. Overall churn rate
SELECT churn_status,
       COUNT(*) AS customers,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS customer_share_pct
FROM customer_metrics
GROUP BY churn_status;

-- 2. Churn by country
SELECT country,
       COUNT(*) AS customers,
       SUM(CASE WHEN churn_status = 'Churned' THEN 1 ELSE 0 END) AS churned_customers,
       ROUND(100.0 * AVG(CASE WHEN churn_status = 'Churned' THEN 1.0 ELSE 0.0 END), 2) AS churn_rate_pct
FROM customer_metrics
GROUP BY country
HAVING COUNT(*) >= 20
ORDER BY churn_rate_pct DESC;

-- 3. Churn by order-frequency band
SELECT frequency_band,
       COUNT(*) AS customers,
       ROUND(100.0 * AVG(CASE WHEN churn_status = 'Churned' THEN 1.0 ELSE 0.0 END), 2) AS churn_rate_pct,
       ROUND(AVG(total_spend), 2) AS average_customer_spend
FROM customer_metrics
GROUP BY frequency_band
ORDER BY churn_rate_pct DESC;

-- 4. Rank customers by value within each churn status
SELECT customer_id, churn_status, total_spend,
       RANK() OVER (PARTITION BY churn_status ORDER BY total_spend DESC) AS value_rank
FROM customer_metrics;
