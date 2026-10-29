import type { Cohort, Filters, Metadata, View } from './types';

export const cohortName: Record<Cohort, string> = {
  frequent: 'Frequent',
  occasional: 'Occasional',
  newly_observed: 'Newly observed',
};
export const num = (value: number | null | undefined, digits = 0) =>
  value == null
    ? '—'
    : value.toLocaleString('en-GB', {
        minimumFractionDigits: digits,
        maximumFractionDigits: digits,
      });
export const pct = (value: number | null | undefined, digits = 1) =>
  value == null ? '—' : `${num(value * 100, digits)}%`;
export const money = (value: number) =>
  new Intl.NumberFormat('en-GB', {
    style: 'currency',
    currency: 'GBP',
    maximumFractionDigits: 0,
  }).format(value);
export const dateLabel = (value: string, year = true) =>
  new Date(value.slice(0, 10) + 'T12:00:00').toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    ...(year ? { year: 'numeric' } : {}),
  });
export const addDays = (value: string, days: number) => {
  const date = new Date(value.slice(0, 10) + 'T12:00:00Z');
  date.setUTCDate(date.getUTCDate() + days);
  return date.toISOString().slice(0, 10);
};
export const relativeDays = (value: number) =>
  value < 1 ? 'Within 24h' : `${num(Math.floor(value))}d ago`;
export const featureNames: Record<string, string> = {
  recency_days: 'Days since last order',
  observed_tenure_days: 'Observed buyer history',
  orders_observed: 'Historical orders',
  spend_observed: 'Historical spend',
  mean_basket_gbp: 'Average basket value',
  mean_distinct_items: 'Basket variety',
  mean_gap_days: 'Average order gap',
  orders_7d: 'Orders · 7 days',
  orders_30d: 'Orders · 30 days',
  orders_90d: 'Orders · 90 days',
  orders_180d: 'Orders · 180 days',
  spend_30d: 'Spend · 30 days',
  spend_90d: 'Spend · 90 days',
  units_30d: 'Units · 30 days',
  cadence_ratio: 'Recency relative to cadence',
  recent_order_share: 'Recent order share',
  recent_spend_share: 'Recent spend share',
};

export function readView(): View {
  const candidate = window.location.hash.slice(1).split('?')[0].replace(/^\//, '');
  return candidate === 'evidence' || candidate === 'method' ? candidate : 'queue';
}
export function initialFilters(meta: Metadata): Filters {
  const params = new URLSearchParams(window.location.hash.split('?')[1]);
  const date = params.get('date') ?? '';
  const model = params.get('model') ?? '';
  const cohort = params.get('cohort') ?? '';
  const capacity = Number(params.get('capacity'));
  return {
    date: meta.dates.includes(date) ? date : meta.dates.at(-1)!,
    model: model in meta.models ? (model as Filters['model']) : meta.selected_model,
    cohort: ['frequent', 'occasional', 'newly_observed'].includes(cohort) ? (cohort as Cohort) : '',
    capacity: [25, 50, 100, 200].includes(capacity) ? capacity : 50,
    search: (params.get('search') ?? '').replace(/\D/g, '').slice(0, 20),
  };
}
export function queueParams(filters: Filters, reveal: boolean): string {
  const params = new URLSearchParams({
    date: filters.date,
    model: filters.model,
    capacity: String(filters.capacity),
    reveal: String(reveal),
  });
  if (filters.search) params.set('search', filters.search);
  if (filters.cohort) params.set('cohort', filters.cohort);
  return params.toString();
}
export function queueHash(filters: Filters): string {
  const params = new URLSearchParams(queueParams(filters, false));
  params.delete('reveal');
  return `#queue?${params}`;
}

export async function getJson<T>(url: string, signal: AbortSignal): Promise<T> {
  const response = await fetch(url, { signal });
  if (!response.ok) {
    let message = `The request could not be completed (${response.status}). Please try again.`;
    try {
      const body = await response.json();
      if (typeof body.detail === 'string') message = body.detail;
    } catch {
      /* Preserve HTTP status. */
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}
