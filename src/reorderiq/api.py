"""Read-only evidence API. No model fitting, pickle loading or external effects."""

import csv
import io
import re
from pathlib import Path
from threading import Lock

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from . import __version__
from .features import FEATURES
from .io import read_json, sha256_file
from .metrics import rank
from .models import MODEL_NAMES

HASHED_UI_ASSET = re.compile(
    r"/assets/ui/assets/[^/]+-[A-Za-z0-9_-]{8,}\.(?:js|css|woff2?|svg|png|jpe?g|webp|avif)"
)


def read_mapping(path: Path) -> dict:
    value = read_json(path)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path.name}")
    return value


class ArtifactStore:
    def __init__(self, run_dir: Path):
        self.manifest = read_mapping(run_dir / "manifest.json")
        if self.manifest.get("status") != "complete":
            raise ValueError("Experiment has not completed")
        if not isinstance(self.manifest.get("files"), dict):
            raise ValueError("Manifest file hashes must be a JSON object")
        for name in [
            "predictions.parquet",
            "orders.parquet",
            "report.json",
            "audit.json",
            "config.json",
            "selection.json",
            "REPORT.md",
        ]:
            if sha256_file(run_dir / name) != self.manifest["files"][name]:
                raise ValueError(f"Artifact hash mismatch: {name}")
        self.report = read_mapping(run_dir / "report.json")
        self.audit = read_mapping(run_dir / "audit.json")
        self.config = read_mapping(run_dir / "config.json")
        selected_model = self.report.get("selected_model")
        if not isinstance(selected_model, str) or selected_model not in MODEL_NAMES:
            raise ValueError("Report has no recognized selected model")
        if not isinstance(self.report.get("source"), str):
            raise ValueError("Report must identify its data source")
        features = self.config.get("features")
        if (
            not isinstance(features, list)
            or not features
            or not all(isinstance(name, str) for name in features)
        ):
            raise ValueError("Configuration must declare its feature names")
        if not set(features).issubset(FEATURES):
            raise ValueError("Configuration contains undeclared historical feature names")
        self.predictions = pd.read_parquet(run_dir / "predictions.parquet")
        self.orders = pd.read_parquet(run_dir / "orders.parquet")
        prediction_columns = {
            "as_of",
            "customer_id",
            "model_id",
            "probability",
            "target",
            "cohort",
            "future_orders",
            "next_order_at",
            *features,
        }
        order_columns = {"customer_id", "ordered_at", "invoice_id", "amount_gbp"}
        if self.predictions.empty or not prediction_columns.issubset(self.predictions.columns):
            raise ValueError("Prediction artifacts do not contain the required buyer records")
        if not order_columns.issubset(self.orders.columns):
            raise ValueError("Order artifact does not contain the required history columns")
        if not self.predictions.as_of.map(lambda value: isinstance(value, str)).all():
            raise ValueError("Prediction snapshot dates must be strings")
        self.orders["ordered_at"] = pd.to_datetime(self.orders.ordered_at)
        self.dates = sorted(self.predictions.as_of.str[:10].unique().tolist())
        self.run_dir = run_dir

    def population(self, date: str | None, model: str | None) -> tuple[pd.DataFrame, str, str]:
        date = date or self.dates[-1]
        model = model or self.report["selected_model"]
        if date not in self.dates:
            raise HTTPException(422, "Choose one of the available historical Mondays")
        if model not in MODEL_NAMES:
            raise HTTPException(422, "Unknown model")
        frame = self.predictions[
            (self.predictions.as_of.str[:10] == date) & (self.predictions.model_id == model)
        ]
        return frame.copy(), date, model


def records(frame: pd.DataFrame) -> list[dict]:
    # JSON-safe nulls without NaN, numpy scalars or timestamp serializer ambiguity.
    import json

    return json.loads(frame.to_json(orient="records", date_format="iso"))


def create_app(runs_dir: Path = Path("runs"), run_id: str | None = None) -> FastAPI:
    app = FastAPI(
        title="ReorderIQ",
        version=__version__,
        description="Local historical buyer reorder evidence",
    )
    app.add_middleware(GZipMiddleware, minimum_size=1024, compresslevel=5)

    @app.middleware("http")
    async def cache_policy(request, call_next):
        response = await call_next(request)
        path = request.url.path
        if path == "/api" or path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        elif path == "/":
            response.headers["Cache-Control"] = "no-cache"
        elif response.status_code in {200, 304} and HASHED_UI_ASSET.fullmatch(path):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        elif path.startswith("/assets/"):
            response.headers["Cache-Control"] = "no-cache"
        return response

    app.state.store = None
    app.state.load_error = None
    app.state.store_lock = Lock()
    web_dir = Path(__file__).parent / "web"

    def get_store() -> ArtifactStore:
        if app.state.store is not None:
            return app.state.store
        # Metadata/evidence arrive concurrently on startup. Verify/load one pinned
        # experiment once rather than allocating a duplicate table per request.
        with app.state.store_lock:
            if app.state.store is not None:
                return app.state.store
            try:
                selected = run_id or read_mapping(runs_dir / "latest.json")["run_id"]
                if (
                    not isinstance(selected, str)
                    or not selected
                    or Path(selected).name != selected
                    or selected in {".", ".."}
                ):
                    raise ValueError("Invalid run identifier")
                app.state.store = ArtifactStore(runs_dir / selected)
                app.state.load_error = None
                return app.state.store
            except (OSError, ValueError, KeyError) as error:
                app.state.load_error = str(error)
                raise HTTPException(
                    503,
                    "No verified experiment is available. Run the local experiment, then retry.",
                ) from error

    @app.get("/api/status")
    def status():
        try:
            store = get_store()
            return {"ready": True, "run_id": store.manifest["run_id"]}
        except HTTPException:
            return {
                "ready": False,
                "message": "Run python -m reorderiq.cli run to create a verified experiment.",
            }

    @app.get("/api/metadata")
    def metadata():
        store = get_store()
        return {
            "run_id": store.manifest["run_id"],
            "dates": store.dates,
            "models": MODEL_NAMES,
            "selected_model": store.report["selected_model"],
            "source": store.report["source"],
            "audit": store.audit,
            "config": store.config,
            "manifest": store.manifest,
        }

    def queue_data(date, model, capacity, search, cohort, reveal):
        store = get_store()
        frame, date, model = store.population(date, model)
        if search:
            frame = frame[frame.customer_id.astype(str).str.contains(search, regex=False)]
        if cohort:
            if cohort not in {"newly_observed", "frequent", "occasional"}:
                raise HTTPException(422, "Unknown buyer cohort")
            frame = frame[frame.cohort == cohort]
        ordered = rank(frame).head(capacity).copy()
        summary = {
            "eligible_buyers": len(frame),
            "selected_buyers": len(ordered),
            "expected_purchasing_buyers": float(ordered.probability.sum()),
            "outcomes_revealed": reveal,
        }
        columns = [
            "customer_id",
            "probability",
            "cohort",
            "recency_days",
            "observed_tenure_days",
            "orders_30d",
            "orders_90d",
            "spend_30d",
            "orders_observed",
            "mean_gap_days",
        ]
        if reveal:
            summary.update(
                {
                    "actual_purchasing_buyers": int(ordered.target.sum()),
                    "precision": float(ordered.target.mean()) if len(ordered) else None,
                    "population_order_rate": float(frame.target.mean()) if len(frame) else None,
                }
            )
            columns += ["target", "next_order_at", "future_orders"]
        ordered["rank"] = range(1, len(ordered) + 1)
        return {
            "date": date,
            "model": model,
            "capacity": capacity,
            "summary": summary,
            "buyers": records(ordered[["rank", *columns]]),
        }

    @app.get("/api/queue")
    def queue(
        date: str | None = None,
        model: str | None = None,
        capacity: int = Query(50, ge=1, le=500),
        search: str = Query("", max_length=20, pattern=r"^\d*$"),
        cohort: str | None = None,
        reveal: bool = False,
    ):
        return queue_data(date, model, capacity, search, cohort, reveal)

    @app.get("/api/export")
    def export(
        date: str | None = None,
        model: str | None = None,
        capacity: int = Query(50, ge=1, le=500),
        search: str = Query("", max_length=20, pattern=r"^\d*$"),
        cohort: str | None = None,
        reveal: bool = False,
    ):
        result = queue_data(date, model, capacity, search, cohort, reveal)
        stream = io.StringIO(newline="")
        if result["buyers"]:
            writer = csv.DictWriter(stream, fieldnames=list(result["buyers"][0]))
            writer.writeheader()
            writer.writerows(result["buyers"])
        else:
            stream.write("rank,customer_id,probability\r\n")
        return Response(
            stream.getvalue(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="reorderiq-{result["date"]}.csv"'
            },
        )

    @app.get("/api/buyers/{customer_id}")
    def buyer(
        customer_id: int, date: str | None = None, model: str | None = None, reveal: bool = False
    ):
        store = get_store()
        frame, date, model = store.population(date, model)
        matched = frame[frame.customer_id == customer_id]
        if matched.empty:
            raise HTTPException(404, "Buyer is not eligible at this snapshot")
        row = matched.iloc[0]
        history = store.orders[
            (store.orders.customer_id == customer_id)
            & (store.orders.ordered_at < pd.Timestamp(date))
        ].sort_values("ordered_at")
        recent = history[history.ordered_at >= pd.Timestamp(date) - pd.Timedelta(days=90)]
        counts = (
            recent.assign(week=recent.ordered_at.dt.to_period("W-SUN").dt.start_time)
            .groupby("week")
            .size()
        )
        week_starts = pd.date_range(
            pd.Timestamp(date) - pd.Timedelta(weeks=12), periods=12, freq="W-MON"
        )
        result = {
            "customer_id": customer_id,
            "date": date,
            "model": model,
            "probability": float(row.probability),
            "cohort": str(row.cohort),
            "features": {key: float(row[key]) for key in store.config["features"]},
            "history": records(history.tail(12)),
            "weekly_orders": [
                {"date": str(week.date()), "orders": int(counts.get(week, 0))}
                for week in week_starts
            ],
            "outcomes_revealed": reveal,
            "history_note": "Only purchases recorded before the selected Monday. Facts describe history; they are not causal explanations.",
        }
        if reveal:
            result["outcome"] = {
                "ordered": bool(row.target),
                "order_count": int(row.future_orders),
                "next_order_at": None if pd.isna(row.next_order_at) else str(row.next_order_at),
            }
        return result

    @app.get("/api/evidence")
    def evidence():
        return get_store().report

    @app.get("/api/report/download")
    def report_download():
        return FileResponse(
            get_store().run_dir / "REPORT.md",
            media_type="text/markdown",
            filename="ReorderIQ-results.md",
        )

    @app.get("/")
    def index():
        return FileResponse(web_dir / "index.html")

    app.mount("/assets", StaticFiles(directory=web_dir, check_dir=False), name="assets")
    return app
