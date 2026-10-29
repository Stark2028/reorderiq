import { useEffect, useRef } from 'react';
import {
  ArrowDownLeft,
  ArrowUpRight,
  ChevronLeft,
  ChevronRight,
  LockKeyhole,
  X,
} from 'lucide-react';
import { AnimatePresence, m, useReducedMotion } from 'motion/react';
import { cohortName, dateLabel, money, num, pct, relativeDays } from '../lib';
import type { Buyer, BuyerDetail } from '../types';
import { HistoryChart } from './Charts';

interface InspectorProps {
  buyer: Buyer | null;
  detail?: BuyerDetail;
  loading: boolean;
  error?: string;
  retry: () => void;
  move: (direction: number) => void;
  index: number;
  total: number;
  reveal: boolean;
}

export function BuyerInspector({
  buyer,
  detail,
  loading,
  error,
  retry,
  move,
  index,
  total,
  reveal,
}: InspectorProps) {
  const reduced = useReducedMotion();
  return (
    <section
      id="buyer-inspector"
      className="buyer-inspector"
      aria-label="Selected buyer history"
      aria-busy={loading}
    >
      <div className="inspector-topline">
        <span>Buyer profile</span>
        <div className="inspector-paging">
          <button
            className="icon-button"
            aria-label="Previous buyer"
            disabled={index <= 0}
            onClick={() => move(-1)}
          >
            <ChevronLeft size={16} />
          </button>
          <span>
            {index + 1} / {total}
          </span>
          <button
            className="icon-button"
            aria-label="Next buyer"
            disabled={index >= total - 1}
            onClick={() => move(1)}
          >
            <ChevronRight size={16} />
          </button>
        </div>
      </div>
      {!buyer ? (
        <div className="empty-state compact">
          <h3>Select a buyer</h3>
          <p>Review the history behind a prediction.</p>
        </div>
      ) : (
        <>
          <div className="buyer-heading">
            <div className="buyer-monogram" aria-hidden="true">
              {String(buyer.customer_id).slice(-2)}
            </div>
            <div>
              <h2 id="buyer-title">Buyer {buyer.customer_id}</h2>
              <span className="cohort-label">{cohortName[buyer.cohort]} buyer</span>
            </div>
          </div>
          {loading ? (
            <div className="detail-skeleton" aria-label="Loading current buyer history">
              <span />
              <span />
              <span />
              <span />
            </div>
          ) : error ? (
            <div className="inline-error" role="alert">
              <h3>History could not be loaded.</h3>
              <p>{error}</p>
              <button className="text-button" onClick={retry}>
                Retry buyer history <ArrowUpRight size={14} />
              </button>
            </div>
          ) : detail ? (
            <AnimatePresence mode="wait" initial={false}>
              <m.div
                key={`${detail.customer_id}-${detail.date}-${detail.model}-${detail.outcomes_revealed}`}
                initial={{ opacity: 0, y: reduced ? 0 : 5 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: reduced ? 0 : 0.16 }}
              >
                <div className="buyer-score">
                  <span className="score-value">{pct(detail.probability)}</span>
                  <span>
                    Seven-day
                    <br />
                    purchase probability
                  </span>
                </div>
                <div className={`outcome-note ${reveal ? 'revealed' : ''}`}>
                  {reveal ? <ArrowDownLeft size={17} /> : <LockKeyhole size={16} />}
                  <div>
                    <strong>
                      {reveal
                        ? detail.outcome?.ordered
                          ? 'An order followed.'
                          : 'No order in this window.'
                        : 'History stops here.'}
                    </strong>
                    <p>
                      {reveal
                        ? detail.outcome?.ordered
                          ? `${detail.outcome.order_count} order${detail.outcome.order_count === 1 ? '' : 's'} · next on ${dateLabel(detail.outcome.next_order_at!, false)}`
                          : 'A probability is not a guarantee.'
                        : `Only records before ${dateLabel(detail.date, false)}.`}
                    </p>
                  </div>
                </div>
                <dl className="buyer-facts">
                  <div>
                    <dt>Last recorded order</dt>
                    <dd>{relativeDays(detail.features.recency_days)}</dd>
                  </div>
                  <div>
                    <dt>Orders · past 30 days</dt>
                    <dd>{num(detail.features.orders_30d)}</dd>
                  </div>
                  <div>
                    <dt>Spend · past 30 days</dt>
                    <dd>{money(detail.features.spend_30d)}</dd>
                  </div>
                  <div>
                    <dt>Typical order gap</dt>
                    <dd>
                      {detail.features.orders_observed > 1
                        ? `${num(detail.features.mean_gap_days, 1)} days`
                        : 'Insufficient history'}
                    </dd>
                  </div>
                </dl>
                <div className="inspector-section">
                  <h3>The last twelve weeks</h3>
                  <HistoryChart weeks={detail.weekly_orders} />
                </div>
                <div className="inspector-section">
                  <div className="section-title">
                    <h3>Recent orders</h3>
                    <span>GBP</span>
                  </div>
                  <ul className="order-history">
                    {detail.history
                      .slice(-4)
                      .reverse()
                      .map((order) => (
                        <li key={order.invoice_id}>
                          <span>
                            <i className="order-dot" />
                            {dateLabel(order.ordered_at, false)}
                          </span>
                          <strong>{money(order.amount_gbp)}</strong>
                        </li>
                      ))}
                  </ul>
                </div>
                <p className="inspector-footnote">
                  {num(detail.features.observed_tenure_days)} days of observed history. These facts
                  describe activity; they do not explain what would cause another purchase.
                </p>
              </m.div>
            </AnimatePresence>
          ) : null}
        </>
      )}
    </section>
  );
}

export function BuyerSheet({
  close,
  returnTo,
  children,
}: {
  close: () => void;
  returnTo: HTMLElement | null;
  children: React.ReactNode;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  const reduced = useReducedMotion();
  useEffect(() => {
    const dialog = ref.current;
    const previousOverflow = document.body.style.overflow;
    dialog?.showModal();
    document.body.style.overflow = 'hidden';
    return () => {
      dialog?.close();
      document.body.style.overflow = previousOverflow;
      requestAnimationFrame(() => returnTo?.focus({ preventScroll: true }));
    };
  }, [returnTo]);
  return (
    <m.dialog
      ref={ref}
      className="buyer-sheet"
      aria-label="Buyer profile"
      onCancel={(event) => {
        event.preventDefault();
        close();
      }}
      onKeyDown={(event) => {
        if (event.key !== 'Tab') return;
        const targets = [
          ...event.currentTarget.querySelectorAll<HTMLElement>(
            'button:not(:disabled),a[href],input:not(:disabled),select:not(:disabled),[tabindex="0"]',
          ),
        ].filter((element) => element.getClientRects().length > 0);
        const first = targets[0],
          last = targets.at(-1);
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last?.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first?.focus();
        }
      }}
      initial={{ opacity: 0, y: reduced ? 0 : 32 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: reduced ? 0 : 20 }}
      transition={{ duration: reduced ? 0 : 0.2, ease: [0.16, 1, 0.3, 1] }}
    >
      <div className="sheet-toolbar">
        <span>Buyer intelligence</span>
        <button
          className="icon-button"
          aria-label="Close buyer profile and return to queue"
          onClick={close}
          autoFocus
        >
          <X size={19} />
        </button>
      </div>
      {children}
    </m.dialog>
  );
}
