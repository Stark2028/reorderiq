export type View = 'queue' | 'evidence' | 'method';
export type Cohort = 'newly_observed' | 'frequent' | 'occasional';
export type ModelId = 'recency' | 'gamma_poisson' | 'logistic' | 'gradient_boosting';

export interface Metadata {
  run_id: string;
  dates: string[];
  models: Record<ModelId, string>;
  selected_model: ModelId;
  source: string;
  audit: {
    raw_lines: number;
    accepted_lines: number;
    orders: number;
    buyers: number;
    exclusions: Record<string, number>;
    workbook_sha256: string;
    observation_end_exclusive: string;
    multi_timestamp_invoices: number;
  };
  config: {
    seed: number;
    features: string[];
    folds: { name: string; fit_end: string; evaluation_start: string; evaluation_end: string }[];
  };
  manifest: { status: string; created_at_utc: string; source_workbook_sha256: string };
}

export interface Filters {
  date: string;
  model: ModelId;
  capacity: number;
  search: string;
  cohort: Cohort | '';
}
export interface Buyer {
  rank: number;
  customer_id: number;
  probability: number;
  cohort: Cohort;
  recency_days: number;
  observed_tenure_days: number;
  orders_30d: number;
  orders_90d: number;
  spend_30d: number;
  orders_observed: number;
  mean_gap_days: number;
  target?: number;
  next_order_at?: string | null;
  future_orders?: number;
}
export interface QueueResult {
  date: string;
  model: ModelId;
  capacity: number;
  buyers: Buyer[];
  summary: {
    eligible_buyers: number;
    selected_buyers: number;
    expected_purchasing_buyers: number;
    outcomes_revealed: boolean;
    actual_purchasing_buyers?: number;
    precision?: number | null;
    population_order_rate?: number | null;
  };
}
export interface BuyerDetail {
  customer_id: number;
  date: string;
  model: ModelId;
  probability: number;
  cohort: Cohort;
  features: Record<string, number>;
  weekly_orders: { date: string; orders: number }[];
  history: {
    invoice_id: string;
    ordered_at: string;
    amount_gbp: number;
    units: number;
    distinct_items: number;
  }[];
  outcomes_revealed: boolean;
  history_note: string;
  outcome?: { ordered: boolean; order_count: number; next_order_at: string | null };
}
export interface Metrics {
  population: number;
  positives: number;
  base_rate: number;
  average_precision: number | null;
  brier: number;
  roc_auc: number | null;
  ece: number;
  selected_50: number;
  captured_50: number;
  precision_50: number;
  recall_50: number | null;
  lift_50: number | null;
  precision_100: number;
  recall_100: number | null;
  lift_100: number | null;
}
export interface CalibrationBin {
  lower: number;
  upper: number;
  count: number;
  predicted: number | null;
  observed: number | null;
}
export interface ModelSummary {
  buyer_weeks: number;
  unique_buyers: number;
  weeks: number;
  macro_weekly: Metrics;
  weekly: (Metrics & { as_of: string })[];
  calibration: CalibrationBin[];
  raw_probability_metrics: { brier: number; ece: number; average_precision: number | null };
  cohorts: Record<
    Cohort,
    { buyer_weeks: number; base_rate: number; brier: number; average_precision: number | null }
  >;
}
export interface Comparison {
  method: string;
  block_weeks: number;
  repetitions: number;
  metrics: Record<
    'average_precision' | 'precision_50' | 'brier',
    { mean_difference: number; lower: number; upper: number; higher_is_better: boolean } | null
  >;
}
export interface Report {
  run_id: string;
  selected_model: ModelId;
  model_names: Record<ModelId, string>;
  snapshot_count: number;
  target: string;
  final: Record<ModelId, ModelSummary>;
  comparison_to_recency: Comparison;
  comparison_to_gamma_poisson: Comparison;
  feature_importance: { feature: string; ap_drop: number }[];
  feature_importance_method: string;
  selection: {
    basis: string;
    candidates: Record<ModelId, { mean_weekly_ap: number; mean_weekly_brier: number }>;
  };
  limitations: string[];
}
