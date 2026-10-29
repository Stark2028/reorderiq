"""Package application source and a verified existing experiment for private transfer."""

import argparse
import tarfile
from pathlib import Path

from reorderiq.io import read_json
from reorderiq.verify import verify_run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(".local/deployment.tar.gz"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    run_id = read_json(root / "runs/latest.json")["run_id"]
    if Path(run_id).name != run_id or run_id in {".", ".."}:
        raise ValueError("Invalid run identifier")
    run = root / "runs" / run_id
    result = verify_run(run)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(args.output, "w:gz") as archive:
        for name in ["Dockerfile", ".dockerignore", "pyproject.toml", "requirements.runtime.lock"]:
            archive.add(root / name, arcname=name)
        for directory in ["src", "deploy"]:
            for path in sorted((root / directory).rglob("*")):
                if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                    archive.add(path, arcname=path.relative_to(root))
        archive.add(root / "runs/latest.json", arcname="artifacts/latest.json")
        for path in sorted(run.iterdir()):
            if path.is_file():
                archive.add(path, arcname=f"artifacts/{run_id}/{path.name}")
    print(f"Verified {result['recomputed_buyer_weeks']} buyer-weeks; wrote {args.output}")


if __name__ == "__main__":
    main()
