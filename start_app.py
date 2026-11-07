#!/usr/bin/env python3
"""VS Code: open this file and click Run Python File, or press F5."""

import argparse
import os
import sys
import threading
import webbrowser
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> None:
    interpreter = ROOT / ".venv/bin/python"
    if Path(sys.prefix).resolve() != (ROOT / ".venv").resolve():
        if not interpreter.exists():
            raise SystemExit("Hiányzik a .venv. Először futtasd: uv sync --locked")
        os.execv(
            str(interpreter),
            [str(interpreter), str(Path(__file__).resolve()), *sys.argv[1:]],
        )
    os.chdir(ROOT)
    parser = argparse.ArgumentParser(description="Kutatóműhely indítása és megnyitása")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("A port 1 és 65535 közötti legyen")
    from industry_research.db import connect
    from industry_research.web import make_server

    with closing(connect(str(ROOT / "data/research.sqlite"))):
        pass
    try:
        server = make_server(str(ROOT / "data/research.sqlite"), args.port)
    except OSError:
        raise SystemExit(
            f"A {args.port} port nem nyitható meg. Zárd be a korábbi futást, vagy adj meg másik portot: --port 8766"
        ) from None
    with server:
        url = f"http://127.0.0.1:{server.server_port}"
        print(f"Kutatóműhely: {url}\nLeállítás: Ctrl+C / VS Code Stop.", flush=True)
        if not args.no_browser:
            threading.Thread(target=webbrowser.open, args=(url,), daemon=True).start()
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
