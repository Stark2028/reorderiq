import asyncio
import gzip
import time
from pathlib import Path

import httpx
import pandas as pd
import pytest

import reorderiq.api as api_module
from reorderiq.api import create_app
from reorderiq.features import FEATURES
from reorderiq.io import sha256_file, write_json

pytestmark = pytest.mark.asyncio


def client_for(runs_dir, run_id=None):
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=create_app(runs_dir, run_id)), base_url="http://test"
    )


@pytest.fixture
def artifacts(tmp_path: Path):
    run = tmp_path / "measured-run"
    run.mkdir()
    rows = []
    for date in ["2011-01-03", "2011-01-10"]:
        for customer in [1, 2]:
            row = {feature: 1.0 for feature in FEATURES}
            row.update(
                {
                    "as_of": date + " 00:00:00",
                    "customer_id": customer,
                    "model_id": "recency",
                    "probability": 0.8 if customer == 1 else 0.2,
                    "target": int(customer == 1),
                    "cohort": "occasional",
                    "next_order_at": "2011-01-04 10:00:00" if customer == 1 else None,
                    "future_orders": int(customer == 1),
                }
            )
            rows.append(row)
    pd.DataFrame(rows).to_parquet(run / "predictions.parquet", index=False)
    pd.DataFrame(
        {
            "customer_id": [1, 1, 1],
            "invoice_id": ["1", "2", "3"],
            "ordered_at": pd.to_datetime(
                ["2011-01-02 10:00", "2011-01-03 00:00", "2011-01-04 10:00"]
            ),
            "amount_gbp": [10.0, 20.0, 30.0],
            "units": [1, 1, 1],
            "distinct_items": [1, 1, 1],
        }
    ).to_parquet(run / "orders.parquet", index=False)
    write_json(
        run / "report.json",
        {"selected_model": "recency", "source": "Test fixture, never a public performance claim"},
    )
    write_json(run / "config.json", {"features": FEATURES})
    write_json(run / "audit.json", {})
    write_json(run / "selection.json", {"selected_model": "recency"})
    (run / "REPORT.md").write_text("Unit test artifact", encoding="utf-8")
    write_json(
        run / "manifest.json",
        {
            "status": "complete",
            "run_id": "measured-run",
            "files": {file.name: sha256_file(file) for file in run.iterdir()},
        },
    )
    write_json(tmp_path / "latest.json", {"run_id": "measured-run"})
    return tmp_path


async def test_hidden_queue_does_not_send_target_or_future_timestamp(artifacts):
    async with client_for(artifacts) as client:
        result = (await client.get("/api/queue?date=2011-01-03")).json()
        assert result["summary"]["selected_buyers"] == 2
        assert "actual_purchasing_buyers" not in result["summary"]
        assert all(
            "target" not in buyer and "next_order_at" not in buyer and "future_orders" not in buyer
            for buyer in result["buyers"]
        )
        revealed = (await client.get("/api/queue?date=2011-01-03&reveal=true")).json()
        assert revealed["summary"]["actual_purchasing_buyers"] == 1


async def test_buyer_history_never_crosses_cutoff_and_outcome_needs_reveal(artifacts):
    async with client_for(artifacts) as client:
        buyer = (await client.get("/api/buyers/1?date=2011-01-03")).json()
        assert len(buyer["history"]) == 1
        assert all(
            pd.Timestamp(row["ordered_at"]) < pd.Timestamp("2011-01-03") for row in buyer["history"]
        )
        assert "outcome" not in buyer
        revealed = (await client.get("/api/buyers/1?date=2011-01-03&reveal=true")).json()
        assert revealed["outcome"]["ordered"] is True
        assert (await client.get("/api/buyers/999?date=2011-01-03")).status_code == 404


async def test_invalid_filters_and_missing_dates_are_explicit(artifacts):
    async with client_for(artifacts) as client:
        for query in [
            "date=2011-01-04",
            "model=unknown",
            "capacity=0",
            "capacity=501",
            "cohort=unknown",
            "search=<script>",
        ]:
            assert (await client.get(f"/api/queue?{query}")).status_code == 422
        empty = (await client.get("/api/queue?search=999")).json()
        assert empty["buyers"] == []
        assert empty["summary"]["selected_buyers"] == 0


async def test_export_respects_reveal_and_empty_population(artifacts):
    async with client_for(artifacts) as client:
        hidden = await client.get("/api/export?date=2011-01-03")
        assert hidden.status_code == 200
        assert "target" not in hidden.text
        assert "next_order_at" not in hidden.text
        assert "target" in (await client.get("/api/export?date=2011-01-03&reveal=true")).text
        assert (await client.get("/api/export?search=999")).text.startswith(
            "rank,customer_id,probability"
        )


async def test_missing_and_tampered_artifacts_are_not_served(artifacts, tmp_path):
    async with client_for(tmp_path / "missing") as client:
        assert (await client.get("/api/status")).json()["ready"] is False
        assert (await client.get("/api/queue")).status_code == 503
    (artifacts / "measured-run" / "report.json").write_text("{}", encoding="utf-8")
    async with client_for(artifacts) as client:
        assert (await client.get("/api/metadata")).status_code == 503


async def test_run_identifier_cannot_escape_run_directory(tmp_path):
    async with client_for(tmp_path, "..") as client:
        assert (await client.get("/api/metadata")).status_code == 503


@pytest.mark.parametrize("payload", [[], None, {"run_id": []}, {"run_id": {}}, {"run_id": 1}])
async def test_malformed_latest_pointer_is_recoverable(tmp_path, payload):
    write_json(tmp_path / "latest.json", payload)
    async with client_for(tmp_path) as client:
        assert (await client.get("/api/status")).json()["ready"] is False
        assert (await client.get("/api/metadata")).status_code == 503


@pytest.mark.parametrize(
    "filename,payload", [("manifest.json", []), ("report.json", []), ("config.json", [])]
)
async def test_malformed_artifact_document_is_recoverable(artifacts, filename, payload):
    run = artifacts / "measured-run"
    write_json(run / filename, payload)
    if filename != "manifest.json":
        from reorderiq.io import read_json

        manifest = read_json(run / "manifest.json")
        manifest["files"][filename] = sha256_file(run / filename)
        write_json(run / "manifest.json", manifest)
    async with client_for(artifacts) as client:
        assert (await client.get("/api/metadata")).status_code == 503


async def test_nonhistorical_feature_cannot_be_served_as_hidden_buyer_fact(artifacts):
    from reorderiq.io import read_json

    run = artifacts / "measured-run"
    write_json(run / "config.json", {"features": [*FEATURES, "target"]})
    manifest = read_json(run / "manifest.json")
    manifest["files"]["config.json"] = sha256_file(run / "config.json")
    write_json(run / "manifest.json", manifest)
    async with client_for(artifacts) as client:
        assert (await client.get("/api/metadata")).status_code == 503


async def test_concurrent_initial_requests_load_verified_run_once(artifacts, monkeypatch):
    original = api_module.ArtifactStore
    loads = 0

    def delayed_store(run_dir):
        nonlocal loads
        loads += 1
        time.sleep(0.05)
        return original(run_dir)

    monkeypatch.setattr(api_module, "ArtifactStore", delayed_store)
    async with client_for(artifacts) as client:
        responses = await asyncio.gather(
            *(
                client.get(route)
                for route in ["/api/metadata", "/api/evidence", "/api/queue", "/api/status"]
            )
        )
    assert all(response.status_code == 200 for response in responses)
    assert loads == 1


@pytest.fixture
def static_client_app(tmp_path, monkeypatch):
    package = tmp_path / "package"
    web = package / "web"
    assets = web / "ui" / "assets"
    assets.mkdir(parents=True)
    document = "<!doctype html><html><body>ReorderIQ review desk</body></html>"
    script = "export const evidence = 'measured retail observations';\n" * 300
    (web / "index.html").write_text(document, encoding="utf-8")
    (assets / "index-abc12345.js").write_text(script, encoding="utf-8", newline="\n")
    (assets / "plain.js").write_text("export const value = 1;", encoding="utf-8")
    monkeypatch.setattr(api_module, "__file__", str(package / "api.py"))
    return create_app(tmp_path / "no-runs"), document, script


async def test_only_content_hashed_assets_have_immutable_cache(static_client_app):
    app, document, _ = static_client_app
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        root = await client.get("/")
        assert root.text == document
        assert root.headers["Cache-Control"] == "no-cache"
        hashed = await client.get("/assets/ui/assets/index-abc12345.js")
        assert hashed.headers["Cache-Control"] == "public, max-age=31536000, immutable"
        ordinary = await client.get("/assets/ui/assets/plain.js")
        assert ordinary.headers["Cache-Control"] == "no-cache"
        missing = await client.get("/assets/ui/assets/missing-abc12345.js")
        assert missing.status_code == 404
        assert "immutable" not in missing.headers.get("Cache-Control", "")


async def test_large_static_response_is_gzipped_and_decodes_to_original(static_client_app):
    app, _, script = static_client_app
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        async with client.stream(
            "GET", "/assets/ui/assets/index-abc12345.js", headers={"Accept-Encoding": "gzip"}
        ) as response:
            compressed = b"".join([part async for part in response.aiter_raw()])
            assert response.headers["Content-Encoding"] == "gzip"
            assert "accept-encoding" in response.headers["Vary"].lower()
        assert gzip.decompress(compressed).decode() == script
        assert len(compressed) < len(script.encode())
        uncompressed = await client.get(
            "/assets/ui/assets/index-abc12345.js", headers={"Accept-Encoding": "identity"}
        )
        assert "Content-Encoding" not in uncompressed.headers
        assert uncompressed.text == script


async def test_api_success_and_error_responses_are_never_cached(artifacts):
    async with client_for(artifacts) as client:
        for route, status in [
            ("/api/metadata", 200),
            ("/api/queue?capacity=0", 422),
            ("/api/unknown", 404),
        ]:
            response = await client.get(route)
            assert response.status_code == status
            assert response.headers["Cache-Control"] == "no-store"
