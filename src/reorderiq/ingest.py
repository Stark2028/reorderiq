"""Official UCI acquisition and auditable positive-order normalization."""

from pathlib import Path
from zipfile import ZipFile

import httpx
import numpy as np
import pandas as pd

from .io import read_json, sha256_file, write_json

SOURCE_URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
SOURCE_PAGE = "https://archive.ics.uci.edu/dataset/502/online+retail+ii"
MAX_BYTES = 150 * 1024 * 1024


def download(data_dir: Path) -> Path:
    raw = data_dir / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    archive = raw / "online_retail_ii.zip"
    if not archive.exists():
        partial = archive.with_suffix(".part")
        total = 0
        with httpx.stream("GET", SOURCE_URL, follow_redirects=True, timeout=120) as response:
            response.raise_for_status()
            with partial.open("wb") as target:
                for chunk in response.iter_bytes(1024 * 1024):
                    total += len(chunk)
                    if total > MAX_BYTES:
                        raise ValueError("Source archive exceeds the 150 MiB acquisition bound")
                    target.write(chunk)
        partial.replace(archive)
    workbook = raw / "online_retail_II.xlsx"
    if not workbook.exists():
        with ZipFile(archive) as source:
            candidates = [x for x in source.infolist() if x.filename.lower().endswith(".xlsx")]
            if len(candidates) != 1 or candidates[0].file_size > MAX_BYTES:
                raise ValueError("Expected one size-bounded Excel workbook in the UCI archive")
            # Write to a fixed path; never extract archive-controlled paths.
            workbook.write_bytes(source.read(candidates[0]))
    write_json(
        raw / "source.json",
        {
            "url": SOURCE_URL,
            "dataset_page": SOURCE_PAGE,
            "citation": "Chen, D. (2012). Online Retail II. UCI. DOI:10.24432/C5CG6D",
            "license": "CC BY 4.0",
            "archive_sha256": sha256_file(archive),
            "workbook_sha256": sha256_file(workbook),
            "workbook_bytes": workbook.stat().st_size,
        },
    )
    return workbook


def normalize(
    raw: pd.DataFrame, observation_end: pd.Timestamp | None = None
) -> tuple[pd.DataFrame, dict]:
    aliases = {
        "invoice": "invoice_id",
        "invoiceno": "invoice_id",
        "stockcode": "stock_code",
        "quantity": "quantity",
        "invoicedate": "ordered_at",
        "price": "price",
        "unitprice": "price",
        "customerid": "customer_id",
        "country": "country",
        "description": "description",
    }
    frame = raw.rename(
        columns={c: aliases.get(c.lower().replace(" ", ""), c) for c in raw.columns}
    ).copy()
    required = {"invoice_id", "stock_code", "quantity", "ordered_at", "price", "customer_id"}
    if not required.issubset(frame.columns):
        raise ValueError(f"Missing source columns: {sorted(required - set(frame.columns))}")
    frame["ordered_at"] = pd.to_datetime(frame["ordered_at"], errors="coerce")
    if frame["ordered_at"].notna().sum() == 0:
        raise ValueError("Source contains no valid timestamps")
    # Conservatively drop the last day: the source does not certify a full day of coverage.
    end = (
        pd.Timestamp(observation_end)
        if observation_end is not None
        else frame["ordered_at"].max().normalize()
    )
    if end.tzinfo is not None:
        raise ValueError(
            "Source timestamps use unspecified local wall time; do not mix aware timestamps"
        )
    audit = {
        "raw_lines": len(frame),
        "observation_end_exclusive": end.isoformat(),
        "exclusions": {},
    }

    def exclude(reason: str, mask: pd.Series) -> None:
        nonlocal frame
        audit["exclusions"][reason] = int(mask.sum())
        frame = frame.loc[~mask].copy()

    exclude("invalid_timestamp", frame["ordered_at"].isna())
    incomplete_invoices = frame.loc[frame["ordered_at"] >= end, "invoice_id"]
    exclude(
        "outside_complete_observation",
        (frame["ordered_at"] >= end) | frame["invoice_id"].isin(incomplete_invoices),
    )
    # Compare original source fields, including description/country, not sheet origin.
    exclude("exact_duplicate_line", frame.duplicated())
    frame["customer_id"] = pd.to_numeric(frame["customer_id"], errors="coerce")
    exclude(
        "invalid_customer",
        frame["customer_id"].isna()
        | ~np.isfinite(frame["customer_id"])
        | (frame["customer_id"] <= 0)
        | (frame["customer_id"] % 1 != 0),
    )
    frame["invoice_id"] = frame["invoice_id"].astype("string").str.strip()
    exclude(
        "cancellation_invoice", frame["invoice_id"].str.upper().str.startswith("C").fillna(False)
    )
    exclude("invalid_invoice", ~frame["invoice_id"].str.fullmatch(r"\d+").fillna(False))
    frame["quantity"] = pd.to_numeric(frame["quantity"], errors="coerce")
    frame["price"] = pd.to_numeric(frame["price"], errors="coerce")
    exclude(
        "nonpositive_or_invalid_quantity",
        frame["quantity"].isna() | ~np.isfinite(frame["quantity"]) | (frame["quantity"] <= 0),
    )
    exclude(
        "nonpositive_or_invalid_price",
        frame["price"].isna() | ~np.isfinite(frame["price"]) | (frame["price"] <= 0),
    )
    frame["stock_code"] = frame["stock_code"].astype("string").str.strip()
    exclude(
        "non_merchandise_code", ~frame["stock_code"].str.fullmatch(r"\d{5}[A-Za-z]*").fillna(False)
    )
    frame["customer_id"] = frame["customer_id"].astype("int64")
    frame["amount_gbp"] = frame["quantity"] * frame["price"]
    # One invoice cannot silently become multiple customer/date events.
    conflicts = frame.groupby("invoice_id").agg(
        customers=("customer_id", "nunique"),
        dates=("ordered_at", "nunique"),
        first=("ordered_at", "min"),
        last=("ordered_at", "max"),
    )
    spans = conflicts["last"] - conflicts["first"]
    if (
        (conflicts.customers > 1)
        | (spans > pd.Timedelta(minutes=5))
        | (conflicts["first"].dt.normalize() != conflicts["last"].dt.normalize())
    ).any():
        raise ValueError(
            "Conflicting customer or timestamp within an invoice; inspect source before proceeding"
        )
    audit["multi_timestamp_invoices"] = int((conflicts.dates > 1).sum())
    audit["max_invoice_span_seconds"] = float(spans.dt.total_seconds().max())
    # Some real invoices span 1-2 minutes. Make the aggregate available only at
    # its LAST line, so an earlier snapshot can never see a later line's amount.
    orders = frame.groupby(["customer_id", "invoice_id"], as_index=False).agg(
        ordered_at=("ordered_at", "max"),
        amount_gbp=("amount_gbp", "sum"),
        units=("quantity", "sum"),
        distinct_items=("stock_code", "nunique"),
    )
    orders = orders.sort_values(["ordered_at", "customer_id", "invoice_id"]).reset_index(drop=True)
    if orders.empty or not np.isfinite(orders[["amount_gbp", "units"]].to_numpy()).all():
        raise ValueError("No valid orders, or nonfinite normalized monetary values")
    audit.update(
        {
            "accepted_lines": len(frame),
            "orders": len(orders),
            "buyers": int(orders.customer_id.nunique()),
            "first_order": orders.ordered_at.min().isoformat(),
            "last_order": orders.ordered_at.max().isoformat(),
            "currency": "GBP",
            "target": "positive merchandise order placed; returns are not netted",
        }
    )
    assert sum(audit["exclusions"].values()) + audit["accepted_lines"] == audit["raw_lines"]
    return orders, audit


def prepare(data_dir: Path, workbook: Path | None = None) -> tuple[Path, dict]:
    workbook = workbook or download(data_dir)
    digest = sha256_file(workbook)
    line_cache = data_dir / "raw" / f"lines-{digest[:12]}.parquet"
    cache_manifest = line_cache.with_suffix(".json")
    if (
        line_cache.exists()
        and cache_manifest.exists()
        and read_json(cache_manifest)["workbook_sha256"] == digest
        and read_json(cache_manifest)["sha256"] == sha256_file(line_cache)
    ):
        raw = pd.read_parquet(line_cache)
        sheet_names = read_json(cache_manifest)["sheets"]
    else:
        print("Reading both UCI workbook sheets...", flush=True)
        sheets = pd.read_excel(workbook, sheet_name=None, engine="openpyxl")
        raw = pd.concat(list(sheets.values()), ignore_index=True)
        sheet_names = list(sheets)
        line_cache.parent.mkdir(parents=True, exist_ok=True)
        # Mixed Excel invoice/stock-code types need a stable parquet representation.
        for column in ["Invoice", "InvoiceNo", "StockCode", "Description", "Country"]:
            if column in raw:
                raw[column] = raw[column].astype("string")
        raw.to_parquet(line_cache, index=False)
        write_json(
            cache_manifest,
            {"sha256": sha256_file(line_cache), "workbook_sha256": digest, "sheets": sheet_names},
        )
    orders, audit = normalize(raw)
    audit.update({"workbook_sha256": digest, "sheets": sheet_names, "source": SOURCE_PAGE})
    processed = data_dir / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    path = processed / "orders.parquet"
    orders.to_parquet(path, index=False)
    audit["orders_sha256"] = sha256_file(path)
    write_json(processed / "audit.json", audit)
    print(f"Accepted {len(orders):,} orders for {audit['buyers']:,} buyers", flush=True)
    return path, audit
