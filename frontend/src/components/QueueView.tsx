import { useRef, useState } from 'react';
import { AnimatePresence, m, useReducedMotion } from 'motion/react';
import {
  ArrowDownToLine,
  ArrowRight,
  Check,
  ChevronLeft,
  ChevronRight,
  Eye,
  EyeOff,
  FilterX,
  Info,
  LockKeyhole,
  Search,
  ShieldCheck,
  SlidersHorizontal,
} from 'lucide-react';
import type { BuyerDetail, Cohort, Filters, Metadata, ModelId, QueueResult } from '../types';
import { addDays, cohortName, dateLabel, money, num, pct, queueParams, relativeDays } from '../lib';
import { useDebounced, useMedia, useResource } from '../hooks';
import { BuyerInspector, BuyerSheet } from './BuyerInspector';

export default function QueueView({
  meta,
  filters,
  setFilters,
}: {
  meta: Metadata;
  filters: Filters;
  setFilters: (value: Filters) => void;
}) {
  const [reveal, setReveal] = useState(false);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [revision, setRevision] = useState(0);
  const [detailRevision, setDetailRevision] = useState(0);
  const [sheetOpen, setSheetOpen] = useState(false);
  const returnTo = useRef<HTMLElement | null>(null);
  const previousDate = useRef(filters.date);
  const reduced = useReducedMotion();
  const compact = useMedia('(max-width: 1100px)');
  const narrow = useMedia('(max-width: 720px)');
  // Also reset before a render caused by URL/back navigation can request revealed data.
  const dateChanged = previousDate.current !== filters.date;
  const effectiveReveal = dateChanged ? false : reveal;
  if (dateChanged) {
    previousDate.current = filters.date;
    setReveal(false);
  }
  const search = useDebounced(filters.search);
  const query = `/api/queue?${queueParams({ ...filters, search }, effectiveReveal)}`;
  const resource = useResource<QueueResult>(query, revision);
  const settling = filters.search !== search;
  const data = !settling ? resource.data : undefined;
  const loading = settling || resource.loading;
  const selected =
    data?.buyers.find((buyer) => buyer.customer_id === selectedId) ?? data?.buyers[0] ?? null;
  const selectedIndex =
    data && selected
      ? data.buyers.findIndex((buyer) => buyer.customer_id === selected.customer_id)
      : -1;
  const detailQuery =
    selected && data
      ? `/api/buyers/${selected.customer_id}?${new URLSearchParams({ date: filters.date, model: filters.model, reveal: String(effectiveReveal) })}`
      : null;
  const detail = useResource<BuyerDetail>(detailQuery, detailRevision);
  const dateIndex = meta.dates.indexOf(filters.date);
  const filtered = Boolean(filters.search || filters.cohort);
  const changeDate = (date: string) => {
    setReveal(false);
    setFilters({ ...filters, date });
  };
  const clearFilters = () => setFilters({ ...filters, search: '', cohort: '' });
  const selectBuyer = (id: number, button: HTMLElement) => {
    setSelectedId(id);
    returnTo.current = button;
    if (compact) setSheetOpen(true);
  };
  const move = (direction: number) => {
    if (data)
      setSelectedId(
        data.buyers[Math.max(0, Math.min(data.buyers.length - 1, selectedIndex + direction))]
          .customer_id,
      );
  };
  const inspector = (
    <BuyerInspector
      buyer={selected}
      detail={detail.data}
      loading={detail.loading}
      error={detail.error}
      retry={() => setDetailRevision((r) => r + 1)}
      move={move}
      index={selectedIndex}
      total={data?.buyers.length ?? 0}
      reveal={effectiveReveal}
    />
  );

  return (
    <section id="queue-view" aria-labelledby="queue-title">
      <div className="page-heading">
        <div>
          <h1 id="queue-title" tabIndex={-1}>
            Review queue<span className="heading-period">.</span>
          </h1>
          <p>A considered view of the next seven days.</p>
        </div>
        <a
          id="export"
          className={`button export-button ${!data ? 'disabled' : ''}`}
          href={data ? `/api/export?${queueParams(filters, effectiveReveal)}` : undefined}
          aria-disabled={!data}
          tabIndex={data ? 0 : -1}
          onClick={(event) => {
            if (!data) event.preventDefault();
          }}
        >
          <ArrowDownToLine size={16} />
          <span>Export queue</span>
        </a>
      </div>

      <div className="query-workbench">
        <div className="query-controls">
          <div className="date-control">
            <label htmlFor="date">Historical Monday</label>
            <div className="date-input">
              <select
                id="date"
                value={filters.date}
                onChange={(event) => changeDate(event.target.value)}
              >
                {meta.dates.map((date) => (
                  <option key={date} value={date}>
                    {dateLabel(date)}
                  </option>
                ))}
              </select>
              <div className="date-steppers">
                <button
                  className="icon-button"
                  aria-label="Previous historical Monday"
                  disabled={dateIndex <= 0}
                  onClick={() => changeDate(meta.dates[dateIndex - 1])}
                >
                  <ChevronLeft size={15} />
                </button>
                <button
                  className="icon-button"
                  aria-label="Next historical Monday"
                  disabled={dateIndex >= meta.dates.length - 1}
                  onClick={() => changeDate(meta.dates[dateIndex + 1])}
                >
                  <ChevronRight size={15} />
                </button>
              </div>
            </div>
          </div>
          <label className="model-control">
            Prediction model
            <select
              id="model"
              value={filters.model}
              onChange={(event) => setFilters({ ...filters, model: event.target.value as ModelId })}
            >
              {Object.entries(meta.models).map(([id, name]) => (
                <option key={id} value={id}>
                  {name}
                  {id === meta.selected_model && !narrow ? ' · selected' : ''}
                </option>
              ))}
            </select>
          </label>
          <label className="capacity-control">
            Review capacity
            <select
              id="capacity"
              value={filters.capacity}
              onChange={(event) => setFilters({ ...filters, capacity: Number(event.target.value) })}
            >
              {[25, 50, 100, 200].map((capacity) => (
                <option key={capacity} value={capacity}>
                  {capacity} buyers
                </option>
              ))}
            </select>
          </label>
          <button
            id="reveal"
            className={`button reveal-button ${effectiveReveal ? 'is-revealed' : ''}`}
            aria-pressed={effectiveReveal}
            disabled={!data && loading}
            onClick={() => setReveal((value) => !value)}
          >
            {effectiveReveal ? <EyeOff size={17} /> : <Eye size={17} />}
            <span>{effectiveReveal ? 'Hide outcomes' : 'Reveal outcomes'}</span>
          </button>
        </div>
        <div className="prediction-boundary">
          <span className="boundary-label">
            <span className={`status-dot ${effectiveReveal ? 'revealed' : ''}`} />
            {effectiveReveal ? 'Observed outcomes' : 'Historical forecast'}
          </span>
          <span>
            {dateLabel(filters.date, false)} <ArrowRight size={13} />{' '}
            {dateLabel(addDays(filters.date, 7), false)}
            <span className="boundary-note"> · seven-day window</span>
          </span>
          <span className="boundary-assurance">
            <ShieldCheck size={14} />
            {effectiveReveal ? 'Observed future orders' : 'Future outcomes hidden'}
          </span>
        </div>
      </div>

      <div id="loading" className="sr-only" role="status" aria-live="polite">
        {loading
          ? 'Updating review queue'
          : resource.error
            ? 'Queue request failed'
            : `${data?.buyers.length ?? 0} buyers ready${effectiveReveal ? ', outcomes revealed' : ', outcomes hidden'}`}
      </div>
      <dl id="summary" className="summary-rail" aria-busy={loading}>
        <div>
          <dt>Eligible buyers{filtered && <span className="small-tag">Filtered</span>}</dt>
          <dd>{data ? num(data.summary.eligible_buyers) : <span className="number-skeleton" />}</dd>
          <small>
            {filtered
              ? 'Within current filters'
              : narrow
                ? 'Active ≤180 days'
                : 'Active in the past 180 days'}
          </small>
        </div>
        <div>
          <dt>
            Expected to order
            <Info
              size={13}
              aria-label="Sum of purchase probabilities in this queue; expected buyers, not expected orders"
            />
          </dt>
          <dd>
            {data ? (
              num(data.summary.expected_purchasing_buyers, 1)
            ) : (
              <span className="number-skeleton" />
            )}
          </dd>
          <small>
            Of {data ? num(data.summary.selected_buyers) : '—'}{' '}
            {narrow ? 'in queue' : 'buyers in this queue'}
          </small>
        </div>
        <div className={effectiveReveal ? 'summary-observed revealed' : 'summary-observed'}>
          <dt>Observed to order{!effectiveReveal && <LockKeyhole size={13} />}</dt>
          <m.dd
            key={String(effectiveReveal)}
            initial={reduced ? false : { opacity: 0.4, clipPath: 'inset(0 0 100% 0)' }}
            animate={{ opacity: 1, clipPath: 'inset(0)' }}
            transition={{ duration: reduced ? 0 : 0.22 }}
          >
            {data ? (
              effectiveReveal ? (
                num(data.summary.actual_purchasing_buyers)
              ) : (
                <span className="hidden-value">Hidden</span>
              )
            ) : (
              <span className="number-skeleton" />
            )}
          </m.dd>
          <small>
            {effectiveReveal && data
              ? `${pct(data.summary.precision)} of queue · ${pct(data.summary.population_order_rate)} of eligible buyers`
              : narrow
                ? 'Reveal to compare'
                : 'Reveal the future to compare'}
          </small>
        </div>
      </dl>

      <div className="review-layout">
        <div className="queue-panel" id="queue-content" aria-busy={loading}>
          <div className="panel-heading">
            <div className="panel-title">
              <SlidersHorizontal size={17} />
              <h2>Your shortlist</h2>
            </div>
            <span id="queue-count">
              {data
                ? `${num(data.buyers.length)} / ${num(data.summary.eligible_buyers)} buyers`
                : 'Preparing shortlist'}
            </span>
          </div>
          <div className="table-filters">
            <label className="search-field">
              <Search size={16} />
              <span className="sr-only">Search buyer ID</span>
              <input
                id="search"
                type="search"
                inputMode="numeric"
                value={filters.search}
                maxLength={20}
                onChange={(event) =>
                  setFilters({ ...filters, search: event.target.value.replace(/\D/g, '') })
                }
                placeholder="Find a buyer by ID"
              />
            </label>
            <label className="cohort-control">
              <span className="sr-only">Buyer cohort</span>
              <select
                id="cohort"
                value={filters.cohort}
                onChange={(event) =>
                  setFilters({ ...filters, cohort: event.target.value as Cohort | '' })
                }
              >
                <option value="">All buyer cohorts</option>
                <option value="frequent">Frequent buyers</option>
                <option value="occasional">Occasional buyers</option>
                <option value="newly_observed">Newly observed</option>
              </select>
            </label>
            {filtered && (
              <button
                className="icon-button clear-filter"
                title="Clear filters"
                aria-label="Clear filters"
                onClick={clearFilters}
              >
                <FilterX size={17} />
              </button>
            )}
          </div>
          {resource.error && !settling ? (
            <div className="empty-state error-state" role="alert">
              <div className="state-symbol">
                <Info size={25} />
              </div>
              <h3>We couldn’t update the shortlist.</h3>
              <p>{resource.error}</p>
              <p className="muted">Exports are paused until the current results are verified.</p>
              <button className="button primary" onClick={() => setRevision((value) => value + 1)}>
                Retry loading <ArrowRight size={15} />
              </button>
            </div>
          ) : loading || !data ? (
            <QueueSkeleton />
          ) : data.buyers.length === 0 ? (
            <div className="empty-state">
              <div className="state-symbol">
                <Search size={25} />
              </div>
              <h3>No buyers in this view.</h3>
              <p>Try another buyer ID or clear your cohort filter.</p>
              <button className="button secondary" onClick={clearFilters}>
                Clear filters <FilterX size={15} />
              </button>
            </div>
          ) : (
            <div className="table-scroll">
              <table className="buyer-table">
                <caption className="sr-only">
                  Buyers ranked by calibrated seven-day purchase probability. Outcomes are{' '}
                  {effectiveReveal ? 'revealed' : 'hidden'}.
                </caption>
                <thead>
                  <tr>
                    <th scope="col" className="rank-column">
                      #
                    </th>
                    <th scope="col">Buyer</th>
                    <th scope="col">Purchase probability</th>
                    <th scope="col" className="hide-tablet">
                      30-day spend
                    </th>
                    <th scope="col" className="hide-small">
                      Last order
                    </th>
                    <th scope="col" className="outcome-column">
                      {effectiveReveal ? (
                        'Outcome'
                      ) : (
                        <span>
                          <LockKeyhole size={11} /> Outcome
                        </span>
                      )}
                    </th>
                  </tr>
                </thead>
                <tbody id="buyers">
                  {data.buyers.map((buyer) => (
                    <tr
                      key={buyer.customer_id}
                      className={buyer.customer_id === selected?.customer_id ? 'selected' : ''}
                    >
                      <td className="rank-column">{String(buyer.rank).padStart(2, '0')}</td>
                      <td>
                        <button
                          className="buyer-link"
                          data-buyer={buyer.customer_id}
                          aria-pressed={buyer.customer_id === selected?.customer_id}
                          aria-controls="buyer-inspector"
                          onClick={(event) => selectBuyer(buyer.customer_id, event.currentTarget)}
                        >
                          <span>Buyer {buyer.customer_id}</span>
                          <small>{cohortName[buyer.cohort]}</small>
                        </button>
                      </td>
                      <td>
                        <div className="probability">
                          <span>{pct(buyer.probability)}</span>
                          <span className="probability-track" aria-hidden="true">
                            <span style={{ width: pct(buyer.probability, 3) }} />
                          </span>
                        </div>
                      </td>
                      <td className="hide-tablet amount-cell">{money(buyer.spend_30d)}</td>
                      <td className="hide-small recency-cell">
                        {relativeDays(buyer.recency_days)}
                      </td>
                      <td className="outcome-cell">
                        {effectiveReveal ? (
                          <span className={`outcome-tag ${buyer.target ? 'ordered' : 'no-order'}`}>
                            {buyer.target ? <Check size={12} /> : null}
                            {buyer.target ? 'Ordered' : 'No order'}
                          </span>
                        ) : (
                          <span className="outcome-hidden" aria-label="Outcome hidden">
                            —
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <div className="table-footnote">
            <ShieldCheck size={14} />
            <p>Ranked purchase propensity. Contacting a buyer may not change whether they order.</p>
          </div>
        </div>
        {!compact && <aside className="desktop-inspector">{inspector}</aside>}
      </div>
      <AnimatePresence>
        {compact && sheetOpen && selected && data && (
          <BuyerSheet close={() => setSheetOpen(false)} returnTo={returnTo.current}>
            {inspector}
          </BuyerSheet>
        )}
      </AnimatePresence>
    </section>
  );
}

function QueueSkeleton() {
  return (
    <div className="queue-skeleton" aria-label="Loading current query">
      <div className="skeleton-header" />
      {Array.from({ length: 7 }, (_, i) => (
        <div className="skeleton-row" key={i}>
          <span />
          <span />
          <span />
        </div>
      ))}
    </div>
  );
}
