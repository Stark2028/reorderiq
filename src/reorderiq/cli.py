"""Local reproduction and serving commands."""

import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(prog="reorderiq")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ["download", "prepare", "run"]:
        command = commands.add_parser(name)
        command.add_argument("--data-dir", type=Path, default=Path("data"))
        if name == "run":
            command.add_argument("--runs-dir", type=Path, default=Path("runs"))
    serve = commands.add_parser("serve")
    serve.add_argument("--runs-dir", type=Path, default=Path("runs"))
    serve.add_argument("--run", default=None)
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8010)
    verify = commands.add_parser("verify")
    verify.add_argument("--runs-dir", type=Path, default=Path("runs"))
    verify.add_argument("--run", default=None)
    args = parser.parse_args()
    if args.command == "download":
        from .ingest import download

        print(download(args.data_dir))
    elif args.command == "prepare":
        from .ingest import prepare

        prepare(args.data_dir)
    elif args.command == "run":
        from .pipeline import run_experiment

        run_experiment(args.data_dir, args.runs_dir)
    elif args.command == "verify":
        import json

        from .io import read_json
        from .verify import verify_run

        selected = args.run or read_json(args.runs_dir / "latest.json")["run_id"]
        print(json.dumps(verify_run(args.runs_dir / selected), indent=2))
    else:
        import uvicorn

        from .api import create_app

        uvicorn.run(create_app(args.runs_dir, args.run), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
