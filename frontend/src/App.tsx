import {
  Component,
  Suspense,
  lazy,
  useEffect,
  useRef,
  useState,
  type ErrorInfo,
  type ReactNode,
} from 'react';
import { AnimatePresence, m, useReducedMotion } from 'motion/react';
import {
  ArrowRight,
  ArrowUpRight,
  BarChart3,
  BookOpenText,
  Check,
  Database,
  ListFilter,
  Moon,
  RotateCcw,
  Sun,
} from 'lucide-react';
import { getJson, initialFilters, queueHash, readView } from './lib';
import type { Filters, Metadata, Report, View } from './types';
import QueueView from './components/QueueView';

const EvidenceView = lazy(() => import('./components/EvidenceView'));
const MethodView = lazy(() => import('./components/MethodView'));
const navigation = [
  { view: 'queue' as const, label: 'Review queue', icon: ListFilter },
  { view: 'evidence' as const, label: 'Model evidence', icon: BarChart3 },
  { view: 'method' as const, label: 'Method & source', icon: BookOpenText },
];

export default function App() {
  const [boot, setBoot] = useState<{ meta: Metadata; report: Report } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [revision, setRevision] = useState(0);
  const [view, setView] = useState<View>(readView);
  const [filters, updateFilters] = useState<Filters | null>(null);
  const [theme, setTheme] = useState(() =>
    document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light',
  );
  const headingFocus = useRef(false);
  const reduced = useReducedMotion();
  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    setError(null);
    Promise.all([
      getJson<Metadata>('/api/metadata', controller.signal),
      getJson<Report>('/api/evidence', controller.signal),
    ])
      .then(([meta, report]) => {
        if (!active) return;
        if (!meta.dates?.length || !report.final?.[report.selected_model])
          throw new Error(
            'The experiment has no complete review data. Verify the local run, then retry.',
          );
        setBoot({ meta, report });
        updateFilters(initialFilters(meta));
      })
      .catch((reason) => {
        if (active && reason.name !== 'AbortError') setError(reason.message);
      });
    return () => {
      active = false;
      controller.abort();
    };
  }, [revision]);
  useEffect(() => {
    const change = () => {
      headingFocus.current = true;
      setView(readView());
      if (boot && readView() === 'queue') updateFilters(initialFilters(boot.meta));
    };
    window.addEventListener('hashchange', change);
    return () => window.removeEventListener('hashchange', change);
  }, [boot]);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem('reorderiq-theme', theme);
    } catch {
      /* Theme stays usable with unavailable storage. */
    }
  }, [theme]);
  useEffect(() => {
    document.title = `${navigation.find((item) => item.view === view)?.label} — ReorderIQ`;
  }, [view]);
  const setFilters = (value: Filters) => {
    updateFilters(value);
    window.history.replaceState(null, '', queueHash(value));
  };
  const navigate = (next: View) => {
    headingFocus.current = true;
    window.location.hash = next === 'queue' && filters ? queueHash(filters).slice(1) : next;
    setView(next);
  };
  return (
    <>
      <a
        className="skip"
        href="#main"
        onClick={(event) => {
          event.preventDefault();
          document.getElementById('main')?.focus();
        }}
      >
        Skip to content
      </a>
      <aside className="rail">
        <a
          className="brand"
          href="#queue"
          onClick={(event) => {
            event.preventDefault();
            navigate('queue');
          }}
          aria-label="ReorderIQ home"
        >
          <span className="brand-mark">
            <svg viewBox="0 0 32 32" aria-hidden="true">
              <path d="M8 25V7h9a5.5 5.5 0 010 11H8m9 0 8 7" />
            </svg>
          </span>
          <span>
            Reorder<span className="brand-iq">IQ</span>
          </span>
        </a>
        <div className="rail-divider" />
        <nav aria-label="Main navigation">
          {navigation.map((item) => (
            <button
              key={item.view}
              data-view={item.view}
              aria-label={item.label}
              aria-current={view === item.view ? 'page' : undefined}
              onClick={() => navigate(item.view)}
            >
              {view === item.view && (
                <m.span
                  className="nav-selection"
                  layoutId="navigation-selection"
                  transition={{ duration: reduced ? 0 : 0.22, ease: [0.16, 1, 0.3, 1] }}
                />
              )}
              <item.icon size={18} />
              <span>{item.label}</span>
              {view === item.view && <span className="nav-dot" />}
            </button>
          ))}
        </nav>
        <div className="rail-bottom">
          <div className="source-label">
            <Database size={15} />
            <span>Public data study</span>
          </div>
          <p>
            UK retail benchmark
            <br />
            2009–2011 · GBP
          </p>
          <span className="rail-motto">Evidence, before action.</span>
          <a
            href="https://archive.ics.uci.edu/dataset/502/online+retail+ii"
            target="_blank"
            rel="noreferrer"
          >
            Explore the source <ArrowUpRight size={13} />
          </a>
        </div>
      </aside>
      <div className="app-shell">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace<span>/</span>
            <strong>{navigation.find((item) => item.view === view)?.label}</strong>
          </div>
          <div className="topbar-actions">
            <span id="run-state" className="run-status">
              <span className="status-dot" />
              {boot
                ? 'Verified experiment'
                : error
                  ? 'Experiment unavailable'
                  : 'Loading experiment'}
            </span>
            <span className="topbar-divider" />
            <button
              className="icon-button theme-toggle"
              aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
              onClick={() => setTheme((value) => (value === 'light' ? 'dark' : 'light'))}
            >
              {theme === 'light' ? <Moon size={17} /> : <Sun size={17} />}
            </button>
          </div>
        </header>
        <main id="main" tabIndex={-1}>
          {error ? (
            <div className="boot-error" role="alert">
              <div className="state-symbol">
                <RotateCcw size={28} />
              </div>
              <h1>A verified run is needed.</h1>
              <p>{error}</p>
              <code>python -m reorderiq.cli run</code>
              <button className="button primary" onClick={() => setRevision((value) => value + 1)}>
                Retry experiment <ArrowRight size={16} />
              </button>
            </div>
          ) : !boot || !filters ? (
            <WorkspaceSkeleton />
          ) : (
            <Suspense fallback={<WorkspaceSkeleton />}>
              <AnimatePresence mode="wait" initial={false}>
                <m.div
                  key={view}
                  onAnimationComplete={() => {
                    if (headingFocus.current && readView() === view) {
                      const heading = document.querySelector<HTMLElement>(`#${view}-title`);
                      if (heading) {
                        heading.focus({ preventScroll: true });
                        headingFocus.current = false;
                      }
                    }
                  }}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: reduced ? 0 : 0.12 }}
                >
                  {view === 'queue' ? (
                    <QueueView meta={boot.meta} filters={filters} setFilters={setFilters} />
                  ) : view === 'evidence' ? (
                    <EvidenceView report={boot.report} />
                  ) : (
                    <MethodView meta={boot.meta} report={boot.report} />
                  )}
                </m.div>
              </AnimatePresence>
            </Suspense>
          )}
          <footer className="page-footer">
            <span>
              <span className="footer-mark">R</span>Independent research. Measured outcomes.
            </span>
            <span>
              <Check size={12} />
              Historical public data <i />
              No causal outreach claims
            </span>
          </footer>
        </main>
      </div>
    </>
  );
}

export function WorkspaceSkeleton() {
  return (
    <div className="workspace-skeleton" role="status" aria-label="Loading workspace">
      <span className="skeleton-title" />
      <span className="skeleton-subtitle" />
      <div className="skeleton-toolbar" />
      <div className="skeleton-content" />
    </div>
  );
}

export class AppBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('ReorderIQ interface error', error, info.componentStack);
  }
  render() {
    return this.state.failed ? (
      <main className="boot-error">
        <h1>The workspace could not render.</h1>
        <p>Reload to restore the verified experiment.</p>
        <button className="button primary" onClick={() => window.location.reload()}>
          Reload workspace
        </button>
      </main>
    ) : (
      this.props.children
    );
  }
}
