"""Check packaged UI completeness and actual same-origin serving behavior."""

import argparse
import json
import re
import tomllib
from pathlib import Path
from zipfile import ZipFile

import httpx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8010")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    version = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"][
        "version"
    ]
    wheel = root / ".local/wheels" / f"reorderiq-{version}-py3-none-any.whl"
    package = root / "src/reorderiq"
    with ZipFile(wheel) as archive:
        entries = archive.namelist()
        shipped = [
            name for name in entries if name.startswith("reorderiq/") and not name.endswith("/")
        ]
        for name in shipped:
            assert archive.read(name) == (package / name.removeprefix("reorderiq/")).read_bytes(), (
                name
            )
        html = archive.read("reorderiq/web/index.html").decode()
        assets = re.findall(r'(?:src|href)="(/assets/ui/[^\"]+)"', html)
        assert assets and all(
            "reorderiq/web/" + path.removeprefix("/assets/") in entries for path in assets
        )
        assert any("motion-LICENSE" in name for name in entries)
        assert any("instrument-serif-OFL" in name for name in entries)
        assert not any(
            name.startswith(("data/", "runs/", "frontend/node_modules/")) for name in entries
        )
    with httpx.Client(base_url=args.url, timeout=15) as client:
        home = client.get("/")
        assert home.status_code == 200 and home.headers.get("cache-control") == "no-cache"
        status = client.get("/api/status")
        assert status.json()["ready"] and status.headers.get("cache-control") == "no-store"
        assert client.get("/openapi.json").json()["info"]["version"] == version
        script = next(path for path in assets if path.endswith(".js"))
        response = client.get(script, headers={"Accept-Encoding": "gzip"})
        assert response.status_code == 200 and response.headers.get("content-encoding") == "gzip"
        assert "immutable" in response.headers.get("cache-control", "")
        assert response.content == (package / "web" / script.removeprefix("/assets/")).read_bytes()
        result = {
            "status": "passed",
            "wheel": wheel.name,
            "wheel_bytes": wheel.stat().st_size,
            "wheel_entries": len(entries),
            "source_matching_package_files": len(shipped),
            "entry_javascript_bytes": len(response.content),
            "entry_javascript_gzip_bytes": response.num_bytes_downloaded,
            "html_cache": home.headers["cache-control"],
            "api_cache": status.headers["cache-control"],
            "hashed_asset_cache": response.headers["cache-control"],
            "run_id": status.json()["run_id"],
        }
    output = root / "verification/distribution.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
