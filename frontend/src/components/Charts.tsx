import { useId, useState } from 'react';
import { m, useReducedMotion } from 'motion/react';
import { dateLabel, num, pct } from '../lib';
import type { CalibrationBin, ModelSummary } from '../types';

export function WeeklyChart({
  chosen,
  baseline,
  name,
}: {
  chosen: ModelSummary;
  baseline: ModelSummary;
  name: string;
}) {
  const id = useId();
  const reduced = useReducedMotion();
  const [index, setIndex] = useState(chosen.weekly.length - 1);
  const current = chosen.weekly[index];
  const x = (i: number) => 48 + (i / Math.max(chosen.weekly.length - 1, 1)) * 430;
  const max = Math.max(
    0.4,
    Math.ceil(
      Math.max(
        ...chosen.weekly.map((w) => w.average_precision ?? 0),
        ...baseline.weekly.map((w) => w.average_precision ?? 0),
      ) * 10,
    ) /
      10 +
      0.1,
  );
  const y = (value: number) => 190 - (value / max) * 156;
  const path = (weeks: ModelSummary['weekly']) =>
    weeks.map((week, i) => `${i ? 'L' : 'M'}${x(i)},${y(week.average_precision ?? 0)}`).join(' ');
  return (
    <div className="chart-content">
      <div className="chart-scale-label">Average precision</div>
      <svg
        className="data-chart"
        viewBox="0 0 500 225"
        role="img"
        aria-labelledby={id}
        tabIndex={0}
        onKeyDown={(event) => {
          if (['ArrowLeft', 'ArrowRight'].includes(event.key)) {
            event.preventDefault();
            setIndex((i) =>
              Math.max(0, Math.min(chosen.weeks - 1, i + (event.key === 'ArrowRight' ? 1 : -1))),
            );
          }
        }}
        onPointerMove={(event) => {
          const bounds = event.currentTarget.getBoundingClientRect();
          const point = ((event.clientX - bounds.left) / bounds.width) * 500;
          setIndex(
            Math.max(
              0,
              Math.min(chosen.weeks - 1, Math.round(((point - 48) / 430) * (chosen.weeks - 1))),
            ),
          );
        }}
      >
        <title id={id}>
          Weekly average precision, {name} versus Gamma–Poisson. Use the arrow keys to inspect each
          week; exact values are in the table below.
        </title>
        {[0, 1, 2, 3, 4].map((tick) => (
          <g key={tick}>
            <line
              className="chart-grid"
              x1="48"
              x2="478"
              y1={y((tick / 4) * max)}
              y2={y((tick / 4) * max)}
            />
            <text x="36" y={y((tick / 4) * max) + 5} textAnchor="end">
              {num((tick / 4) * max, 2)}
            </text>
          </g>
        ))}
        <path className="chart-line baseline-line" d={path(baseline.weekly)} />
        <m.path
          className="chart-line selected-line"
          d={path(chosen.weekly)}
          initial={reduced ? false : { pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 0.45, ease: 'easeOut' }}
        />
        <line className="chart-guide" x1={x(index)} x2={x(index)} y1="30" y2="192" />
        <circle
          className="selected-point"
          cx={x(index)}
          cy={y(current.average_precision ?? 0)}
          r="4.5"
        />
        <circle
          className="baseline-point"
          cx={x(index)}
          cy={y(baseline.weekly[index].average_precision ?? 0)}
          r="4"
        />
        <text x="48" y="217">
          {dateLabel(chosen.weekly[0].as_of, false)}
        </text>
        <text x="478" y="217" textAnchor="end">
          {dateLabel(chosen.weekly.at(-1)!.as_of, false)}
        </text>
      </svg>
      <div className="chart-readout" aria-live="polite">
        <span>{dateLabel(current.as_of)}</span>
        <span>
          <i className="legend-line" />
          {num(current.average_precision, 3)}
        </span>
        <span>
          <i className="legend-line brass" />
          {num(baseline.weekly[index].average_precision, 3)}
        </span>
      </div>
      <div className="chart-legend">
        <span>
          <i className="legend-line" />
          {name}
        </span>
        <span>
          <i className="legend-line brass" />
          Gamma–Poisson
        </span>
      </div>
    </div>
  );
}

export function CalibrationChart({ bins }: { bins: CalibrationBin[] }) {
  const id = useId();
  const [selected, setSelected] = useState<number | null>(null);
  const x = (v: number) => 54 + v * 420,
    y = (v: number) => 190 - v * 156;
  const populated = bins.filter(
    (bin) => bin.count && bin.predicted != null && bin.observed != null,
  );
  const current = selected == null ? null : populated[selected];
  return (
    <div className="chart-content">
      <div className="chart-scale-label">Observed purchase rate</div>
      <svg className="data-chart" viewBox="0 0 500 225" role="img" aria-labelledby={id}>
        <title id={id}>
          Reliability diagram. Equal-size points represent probability bins. Exact bin counts and
          rates are available below.
        </title>
        {[0, 0.25, 0.5, 0.75, 1].map((tick) => (
          <g key={tick}>
            <line className="chart-grid" x1="54" x2="474" y1={y(tick)} y2={y(tick)} />
            <text x="42" y={y(tick) + 5} textAnchor="end">
              {pct(tick, 0)}
            </text>
            <text x={x(tick)} y="217" textAnchor="middle">
              {pct(tick, 0)}
            </text>
          </g>
        ))}
        <path className="baseline-line ideal-line" d={`M${x(0)} ${y(0)}L${x(1)} ${y(1)}`} />
        {populated.map((bin, i) => (
          <circle
            className={`calibration-point ${selected === i ? 'active' : ''}`}
            key={bin.lower}
            cx={x(bin.predicted!)}
            cy={y(bin.observed!)}
            r="5"
            onPointerEnter={() => setSelected(i)}
          >
            <title>
              {num(bin.count)} buyer-weeks · {pct(bin.predicted)} predicted · {pct(bin.observed)}{' '}
              observed
            </title>
          </circle>
        ))}
      </svg>
      <div className="chart-axis-label">Predicted purchase probability</div>
      <div className="calibration-readout">
        {current
          ? `${num(current.count)} buyer-weeks · ${pct(current.predicted)} predicted / ${pct(current.observed)} observed`
          : 'Each point is a populated probability bin; the diagonal is ideal agreement.'}
      </div>
    </div>
  );
}

export function HistoryChart({ weeks }: { weeks: { date: string; orders: number }[] }) {
  const id = useId();
  const max = Math.max(1, ...weeks.map((w) => w.orders));
  return (
    <div className="history-plot">
      <div className="history-labels">
        <span>Orders / week</span>
        <span>Max {max}</span>
      </div>
      <svg viewBox="0 0 320 92" role="img" aria-labelledby={id}>
        <title id={id}>
          {weeks.map((w) => `${dateLabel(w.date, false)}: ${w.orders} orders`).join('; ')}
        </title>
        <line x1="4" x2="316" y1="78" y2="78" className="chart-grid" />
        {weeks.map((week, i) => (
          <g key={week.date}>
            <rect
              x={5 + i * 26}
              y={78 - (week.orders / max) * 50}
              width="15"
              height={Math.max(week.orders ? 2 : 0, (week.orders / max) * 50)}
              rx="2"
            />
            <text
              x={12.5 + i * 26}
              y={Math.max(14, 70 - (week.orders / max) * 50)}
              textAnchor="middle"
            >
              {week.orders}
            </text>
          </g>
        ))}
      </svg>
      <div className="history-range">
        <span>{dateLabel(weeks[0].date, false)}</span>
        <span>{dateLabel(weeks.at(-1)!.date, false)}</span>
      </div>
    </div>
  );
}
