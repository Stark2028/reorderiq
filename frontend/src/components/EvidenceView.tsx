import { useState } from 'react';
import { ArrowDownToLine, ArrowUpRight, Check, ChevronDown, ShieldCheck } from 'lucide-react';
import { featureNames, cohortName, dateLabel, num, pct } from '../lib';
import type { ModelId, Report } from '../types';
import { CalibrationChart, WeeklyChart } from './Charts';

export default function EvidenceView({ report }: { report: Report }) {
  const [details, setDetails] = useState<'weekly' | 'calibration'>('weekly');
  const selected = report.selected_model;
  const result = report.final[selected];
  const baseline = report.final.gamma_poisson;
  const comparison = report.comparison_to_gamma_poisson.metrics;
  const topFeatures = report.feature_importance.slice(0, 7);
  const maxImportance = Math.max(0.001, ...topFeatures.map((item) => item.ap_drop));
  return (
    <section id="evidence-view" aria-labelledby="evidence-title">
      <div className="page-heading">
        <div>
          <h1 id="evidence-title" tabIndex={-1}>
            Model evidence<span className="heading-period">.</span>
          </h1>
          <p>A ranking is only as useful as the evidence behind it.</p>
        </div>
        <a className="button export-button" href="/api/report/download">
          <ArrowDownToLine size={16} />
          Download report
        </a>
      </div>
      <div className="evidence-contract">
        <div className="evidence-seal">
          <ShieldCheck size={23} />
        </div>
        <div>
          <h2>{report.model_names[selected]}</h2>
          <p>Frozen development selection · final temporal holdout</p>
        </div>
        <div className="evidence-population">
          <strong>{num(result.weeks)} weeks</strong>
          <span>
            {num(result.unique_buyers)} distinct buyers · {num(result.buyer_weeks)} buyer-weeks
          </span>
        </div>
      </div>
      <p className="scope-note">
        This view evaluates the development-selected model, independently of the model selected in
        your review queue.
      </p>

      <section className="evidence-panel comparison-panel" aria-labelledby="comparison-title">
        <div className="panel-heading">
          <div>
            <h2 id="comparison-title">Four approaches. The same test.</h2>
            <p>Metrics are measured per week, then equally averaged.</p>
          </div>
          <span className="quiet-badge">Final holdout</span>
        </div>
        <div className="results-scroll">
          <table className="results-table">
            <caption className="sr-only">
              Final holdout comparison. Average precision and Brier loss are scores, not accuracy
              percentages.
            </caption>
            <thead>
              <tr>
                <th scope="col">Candidate</th>
                <th scope="col">Average precision</th>
                <th scope="col">Brier loss ↓</th>
                <th scope="col">Precision @50</th>
                <th scope="col">Lift @50</th>
              </tr>
            </thead>
            <tbody>
              {(Object.keys(report.final) as ModelId[]).map((model) => {
                const metrics = report.final[model].macro_weekly;
                return (
                  <tr key={model} className={model === selected ? 'chosen' : ''}>
                    <td>
                      <span className="model-name">
                        {report.model_names[model]}
                        {model === selected && (
                          <span className="selected-tag">
                            <Check size={11} />
                            Selected
                          </span>
                        )}
                      </span>
                      <small>
                        {model === 'recency'
                          ? 'Simple ranking rule'
                          : model === 'gamma_poisson'
                            ? 'Statistical baseline'
                            : model === 'logistic'
                              ? 'Linear classifier'
                              : 'Nonlinear classifier'}
                      </small>
                    </td>
                    <td>{num(metrics.average_precision, 4)}</td>
                    <td>{num(metrics.brier, 4)}</td>
                    <td>{pct(metrics.precision_50)}</td>
                    <td>{num(metrics.lift_50, 2)}×</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <div className="evidence-table-foot">
          <span>
            <ShieldCheck size={14} />
            Selection was locked before this period was evaluated.
          </span>
          <span>Lift measures predictive enrichment, not outreach effects.</span>
        </div>
      </section>

      <div className="evidence-charts">
        <section className="evidence-panel chart-panel">
          <div className="panel-heading">
            <div>
              <h2>Performance through time</h2>
              <p>Ranking quality across {result.weeks} later Mondays.</p>
            </div>
            <span className="chart-unit">AP</span>
          </div>
          <WeeklyChart chosen={result} baseline={baseline} name={report.model_names[selected]} />
        </section>
        <section className="evidence-panel chart-panel">
          <div className="panel-heading">
            <div>
              <h2>Probability, checked</h2>
              <p>Do predicted rates agree with observed purchases?</p>
            </div>
            <span className="chart-unit">0–1</span>
          </div>
          <CalibrationChart bins={result.calibration} />
        </section>
      </div>

      <section className="interpretation-strip">
        <div className="interpretation-symbol">
          <ArrowUpRight size={22} />
        </div>
        <div>
          <h3>The gain deserves context.</h3>
          <p>
            Against Gamma–Poisson, mean weekly AP changes by{' '}
            <strong>{num(comparison.average_precision?.mean_difference, 4)}</strong> (temporal
            interval {num(comparison.average_precision?.lower, 4)} to{' '}
            {num(comparison.average_precision?.upper, 4)}). The precision@50 difference is{' '}
            <strong>
              {comparison.precision_50
                ? num(comparison.precision_50.mean_difference * 100, 2)
                : '—'}{' '}
              percentage points
            </strong>
            , with an interval from{' '}
            {comparison.precision_50 ? num(comparison.precision_50.lower * 100, 2) : '—'} to{' '}
            {comparison.precision_50 ? num(comparison.precision_50.upper * 100, 2) : '—'} points.
            The interval spans zero; the gain in a top-50 queue remains uncertain in this sample.
          </p>
          <small>
            Paired four-week moving blocks · {num(report.comparison_to_gamma_poisson.repetitions)}{' '}
            resamples · descriptive stability, not a causal claim
          </small>
        </div>
      </section>

      <div className="evidence-charts">
        <section className="evidence-panel signals-panel">
          <div className="panel-heading">
            <div>
              <h2>What the ranking uses</h2>
              <p>Average precision lost when one feature is shuffled.</p>
            </div>
          </div>
          <div className="importance-list">
            {topFeatures.map((feature) => (
              <div className="importance-row" key={feature.feature}>
                <span>{featureNames[feature.feature] ?? feature.feature.replaceAll('_', ' ')}</span>
                <div className="importance-track" aria-hidden="true">
                  <span
                    style={{ width: `${(Math.max(0, feature.ap_drop) / maxImportance) * 100}%` }}
                  />
                </div>
                <strong>{num(feature.ap_drop, 3)}</strong>
              </div>
            ))}
          </div>
          <p className="panel-note">
            Predictive associations only. Correlated features can share information; a negative
            value means shuffling improved the sampled score.
          </p>
        </section>
        <section className="evidence-panel cohort-panel">
          <div className="panel-heading">
            <div>
              <h2>Different buyer histories</h2>
              <p>Pooled buyer-week metrics; each cohort has its own base rate.</p>
            </div>
          </div>
          <div className="results-scroll">
            <table className="results-table cohort-table">
              <thead>
                <tr>
                  <th>Cohort</th>
                  <th>Buyer-weeks</th>
                  <th>Order rate</th>
                  <th>AP</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(result.cohorts).map(([cohort, value]) => (
                  <tr key={cohort}>
                    <td>{cohortName[cohort as keyof typeof cohortName]}</td>
                    <td>{num(value.buyer_weeks)}</td>
                    <td>{pct(value.base_rate)}</td>
                    <td>{num(value.average_precision, 3)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="panel-note">
            Newly observed: ≤30 days of history. Frequent: ≥4 orders in 90 days. Remaining buyers
            are occasional. AP should be interpreted alongside prevalence.
          </p>
        </section>
      </div>

      <details className="evidence-panel exact-data">
        <summary>
          Inspect the exact values <ChevronDown size={16} />
        </summary>
        <div className="data-tabs" role="group" aria-label="Evidence data table">
          <button
            className={details === 'weekly' ? 'active' : ''}
            aria-pressed={details === 'weekly'}
            onClick={() => setDetails('weekly')}
          >
            Weekly results
          </button>
          <button
            className={details === 'calibration' ? 'active' : ''}
            aria-pressed={details === 'calibration'}
            onClick={() => setDetails('calibration')}
          >
            Calibration bins
          </button>
        </div>
        <div className="results-scroll">
          {details === 'weekly' ? (
            <table className="results-table">
              <thead>
                <tr>
                  <th>Historical Monday</th>
                  <th>Eligible buyers</th>
                  <th>Order rate</th>
                  <th>AP</th>
                  <th>Precision @50</th>
                </tr>
              </thead>
              <tbody>
                {result.weekly.map((week) => (
                  <tr key={week.as_of}>
                    <td>{dateLabel(week.as_of)}</td>
                    <td>{num(week.population)}</td>
                    <td>{pct(week.base_rate)}</td>
                    <td>{num(week.average_precision, 4)}</td>
                    <td>{pct(week.precision_50)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <table className="results-table">
              <thead>
                <tr>
                  <th>Probability bin</th>
                  <th>Buyer-weeks</th>
                  <th>Predicted rate</th>
                  <th>Observed rate</th>
                </tr>
              </thead>
              <tbody>
                {result.calibration.map((bin) => (
                  <tr key={bin.lower}>
                    <td>
                      {pct(bin.lower, 0)}–{pct(bin.upper, 0)}
                    </td>
                    <td>{num(bin.count)}</td>
                    <td>{pct(bin.predicted)}</td>
                    <td>{pct(bin.observed)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </details>
    </section>
  );
}
