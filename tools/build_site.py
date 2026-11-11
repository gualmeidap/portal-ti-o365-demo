"""Build the static site for GitHub Pages.

`_site/` gets the shell page (web/), the Flask app and its templates, and the
pure-Python wheels Flask needs. web/shell.js loads them into Pyodide, so the
whole portal runs in the visitor's browser. No server involved.

    python tools/build_site.py            # then: python -m http.server -d _site
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_site"
# Pure-Python wheels (Jinja2, MarkupSafe, click and sqlite3 ship with Pyodide).
WHEELS = ["flask==3.1.3", "werkzeug==3.1.5", "itsdangerous==2.2.0", "blinker==1.9.0"]


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "web", OUT)
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    py = OUT / "py"
    fontes = [ROOT / "app.py", ROOT / "navegador.py"]
    fontes += sorted((ROOT / "portal_demo").rglob("*.py"))
    fontes += sorted((ROOT / "templates").glob("*.html"))
    files = []
    for src in fontes:
        rel = src.relative_to(ROOT).as_posix()
        (py / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, py / rel)
        files.append(rel)

    wheels_dir = py / "wheels"
    wheels_dir.mkdir(parents=True)
    subprocess.run([sys.executable, "-m", "pip", "download", "--quiet", "--no-deps", "--only-binary=:all:",
                    "--dest", str(wheels_dir), *WHEELS], check=True)
    wheels = sorted(p.name for p in wheels_dir.glob("*.whl"))
    if len(wheels) != len(WHEELS) or not all(w.endswith("-none-any.whl") for w in wheels):
        raise SystemExit(f"expected {len(WHEELS)} pure-Python wheels, got {wheels}")

    (py / "manifest.json").write_text(json.dumps({"files": files, "wheels": wheels}, indent=1), encoding="utf-8")
    print(f"built {OUT} ({len(files)} files, wheels: {', '.join(wheels)})")


if __name__ == "__main__":
    main()
