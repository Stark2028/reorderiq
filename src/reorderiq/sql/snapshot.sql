-- All history predicates are strictly before :as_of. No future-dependent eligibility.
WITH history AS (
  SELECT *, julianday(ordered_at) - julianday(LAG(ordered_at) OVER
      (PARTITION BY customer_id ORDER BY ordered_at, invoice_id)) AS gap_days
  FROM orders WHERE ordered_at < :as_of
), aggregate_history AS (
  SELECT customer_id,
    julianday(:as_of) - julianday(MAX(ordered_at)) AS recency_days,
    julianday(:as_of) - julianday(MIN(ordered_at)) AS observed_tenure_days,
    COUNT(*) AS orders_observed,
    SUM(amount_gbp) AS spend_observed,
    AVG(amount_gbp) AS mean_basket_gbp,
    AVG(distinct_items) AS mean_distinct_items,
    COALESCE(AVG(gap_days), 0.0) AS mean_gap_days,
    SUM(CASE WHEN ordered_at >= datetime(:as_of, '-7 days') THEN 1 ELSE 0 END) AS orders_7d,
    SUM(CASE WHEN ordered_at >= datetime(:as_of, '-30 days') THEN 1 ELSE 0 END) AS orders_30d,
    SUM(CASE WHEN ordered_at >= datetime(:as_of, '-90 days') THEN 1 ELSE 0 END) AS orders_90d,
    SUM(CASE WHEN ordered_at >= datetime(:as_of, '-180 days') THEN 1 ELSE 0 END) AS orders_180d,
    SUM(CASE WHEN ordered_at >= datetime(:as_of, '-30 days') THEN amount_gbp ELSE 0 END) AS spend_30d,
    SUM(CASE WHEN ordered_at >= datetime(:as_of, '-90 days') THEN amount_gbp ELSE 0 END) AS spend_90d,
    SUM(CASE WHEN ordered_at >= datetime(:as_of, '-30 days') THEN units ELSE 0 END) AS units_30d
  FROM history GROUP BY customer_id
), future AS (
  SELECT customer_id, COUNT(*) AS future_orders, MIN(ordered_at) AS next_order_at
  FROM orders WHERE ordered_at >= :as_of AND ordered_at < :label_end
  GROUP BY customer_id
)
SELECT h.*, :as_of AS as_of, :label_end AS label_end,
  CASE WHEN COALESCE(f.future_orders, 0) > 0 THEN 1 ELSE 0 END AS target,
  COALESCE(f.future_orders, 0) AS future_orders, f.next_order_at
FROM aggregate_history h LEFT JOIN future f USING (customer_id)
WHERE h.recency_days <= :active_days
ORDER BY h.customer_id
