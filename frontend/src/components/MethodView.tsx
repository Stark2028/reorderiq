import { ArrowUpRight, Check, Database, Fingerprint, Layers3, LockKeyhole } from 'lucide-react';
import { dateLabel, num } from '../lib';
import type { Metadata, Report } from '../types';

export default function MethodView({ meta, report }: { meta: Metadata; report: Report }) {
  const final = meta.config.folds.find((fold) => fold.name === 'final')!;
  return (
    <section id="method-view" aria-labelledby="method-title">
      <div className="page-heading">
        <div>
          <h1 id="method-title" tabIndex={-1}>
            Method & source<span className="heading-period">.</span>
          </h1>
          <p>A clear boundary between what is observed and what is inferred.</p>
        </div>
        <a
          className="button export-button"
          href="https://archive.ics.uci.edu/dataset/502/online+retail+ii"
          target="_blank"
          rel="noreferrer"
        >
          View source <ArrowUpRight size={16} />
        </a>
      </div>
      <div className="method-layout">
        <div className="method-main">
          <section className="evidence-panel method-protocol">
            <div className="method-icon">
              <LockKeyhole size={21} />
            </div>
            <h2>
              One Monday.
              <br />
              <span className="serif-italic">One measurable question.</span>
            </h2>
            <p>
              Using only orders recorded before Monday at midnight, estimate whether an existing
              buyer will place a positive merchandise order during the following seven days.
            </p>
            <p>
              The window includes Monday and ends just before the next Monday. Buyers are eligible
              if their last observed order was within 180 days. Only fully observed windows are
              evaluated.
            </p>
            <div className="protocol-timeline">
              <div>
                <span className="protocol-point" />
                <strong>Fit</strong>
                <p>
                  Labels mature by
                  <br />
                  {dateLabel(final.fit_end)}
                </p>
              </div>
              <div>
                <span className="protocol-point" />
                <strong>Calibrate</strong>
                <p>
                  {dateLabel(final.fit_end, false)} — {dateLabel(final.evaluation_start, false)}
                  <br />
                  Independent interval
                </p>
              </div>
              <div>
                <span className="protocol-point final" />
                <strong>Evaluate</strong>
                <p>
                  {dateLabel(final.evaluation_start, false)} — {dateLabel(final.evaluation_end)}
                  <br />
                  Frozen models
                </p>
              </div>
            </div>
            <p className="method-aside">
              Two earlier temporal folds select the model before the final holdout is evaluated.
              Repeated buyers may appear across time periods; this measures later behavior of
              observed buyers.
            </p>
          </section>
          <section className="evidence-panel scope-panel">
            <h2>What this study can establish</h2>
            <div className="scope-row">
              <Check size={17} />
              <p>
                How well a ranking captures observed future purchases, and whether predicted
                probabilities match purchase rates.
              </p>
            </div>
            <div className="scope-row">
              <Check size={17} />
              <p>
                How performance varies across weeks and buyer histories, with the same population
                for every candidate.
              </p>
            </div>
            <div className="scope-boundary">
              <h3>Where the evidence ends</h3>
              <p>
                Purchase propensity does not tell us whether a call caused an order. The dataset has
                no randomized contact history. A controlled outreach experiment would be needed to
                establish incremental sales.
              </p>
            </div>
            <ul className="limitation-list">
              {report.limitations.map((limit) => (
                <li key={limit}>{limit}.</li>
              ))}
            </ul>
          </section>
        </div>
        <aside className="method-side">
          <section className="evidence-panel source-panel">
            <Database size={21} />
            <h2>
              Real records.
              <br />
              Documented scope.
            </h2>
            <p>
              UCI Online Retail II follows a UK giftware retailer from 2009 to 2011. Many customers
              were wholesalers; the records do not establish that every buyer is a business.
            </p>
            <dl className="source-facts">
              <div>
                <dt>Source invoice lines</dt>
                <dd>{num(meta.audit.raw_lines)}</dd>
              </div>
              <div>
                <dt>Accepted orders</dt>
                <dd>{num(meta.audit.orders)}</dd>
              </div>
              <div>
                <dt>Observed buyers</dt>
                <dd>{num(meta.audit.buyers)}</dd>
              </div>
              <div>
                <dt>Weekly snapshots</dt>
                <dd>{num(report.snapshot_count)}</dd>
              </div>
            </dl>
            <p className="panel-note">
              GBP throughout. Invoices are orders; rows are line items. This is a public benchmark,
              not Udaan data.
            </p>
            <details className="audit-details">
              <summary>Sequential exclusion audit</summary>
              <dl>
                {Object.entries(meta.audit.exclusions).map(([reason, count]) => (
                  <div key={reason}>
                    <dt>{reason.replaceAll('_', ' ')}</dt>
                    <dd>{num(count)}</dd>
                  </div>
                ))}
              </dl>
            </details>
            <p className="source-citation">
              Chen, D. (2012). Online Retail II.
              <br />
              DOI: 10.24432/C5CG6D · CC BY 4.0
            </p>
          </section>
          <section className="evidence-panel provenance-panel">
            <Fingerprint size={21} />
            <h2>Evidence you can trace.</h2>
            <p>
              Every completed experiment preserves its source, configuration, frozen selection,
              predictions, and artifact hashes. No model trains inside the app.
            </p>
            <div className="provenance-id">
              <span>Run identifier</span>
              <code>{meta.run_id}</code>
              <span>Workbook SHA-256</span>
              <code>{meta.audit.workbook_sha256.slice(0, 24)}…</code>
            </div>
          </section>
          <section className="motivation-note">
            <Layers3 size={18} />
            <div>
              <h3>Built around a real question.</h3>
              <p>
                Inspired by{' '}
                <a href="https://arxiv.org/html/2403.07843v1" target="_blank" rel="noreferrer">
                  published predictive-buying research at Udaan
                </a>
                . An independent implementation on public data.
              </p>
            </div>
          </section>
        </aside>
      </div>
    </section>
  );
}
