"""Gestor ficticio para pruebas de interacción; no accede a Codex ni a la red."""

import argparse
import json
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("action", choices=("search", "install"))
    parser.add_argument("name")
    args = parser.parse_args()
    data = json.loads(args.state.read_text(encoding="utf-8"))
    data.setdefault("calls", []).append({"action": args.action, "name": args.name})
    if args.action == "search" and data.get("search_error"):
        args.state.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print("No se pudo consultar el catálogo simulado", file=sys.stderr)
        raise SystemExit(1)
    if args.action == "install":
        if args.name != data["plugin"]["name"]:
            raise SystemExit("Identidad desconocida")
        data["plugin"].update(installed=True, status="ENABLED")
    args.state.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"plugins": [data["plugin"]]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
