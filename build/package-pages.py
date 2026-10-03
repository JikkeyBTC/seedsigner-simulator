"""Assemble a self-contained GitHub Pages artifact from the pinned build."""

import argparse
from pathlib import Path
import shutil
from package_licenses import package_licenses


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build/pages")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        parser.error("output must be a new or empty directory")
    required = [ROOT / "src/web/pyodide/pyodide.js", ROOT / "src/web/pyodide/pyodide.asm.wasm"]
    for firmware in ("smartcard", "stock"):
        required += [ROOT / "build/out" / f"wallet-{firmware}{suffix}"
                     for suffix in (".zip", ".zip.manifest", ".build-info.json")]
    for source in required:
        if not source.is_file():
            parser.error(f"missing build input: {source.relative_to(ROOT)}")
    shutil.copytree(ROOT / "src/web", output, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "doom.js",
                                                  "doom.wasm", "doom-run.js", "*.wad"))
    for source in (ROOT / "src/shims").glob("browser_*.py"):
        shutil.copy2(source, output / source.name)
    for source in required[2:]:
        shutil.copy2(source, output / source.name)
    # Pages is a wallet-only distribution. Local DOOM builds and WADs have
    # separate licenses and must not enter this artifact through copytree.
    if not (output / "doom-run.js").exists():
        (output / "doom-run.js").write_text("// DOOM is not included in this wallet-only build.\n", encoding="utf-8")
    (output / ".nojekyll").touch()
    # Serve the simulator itself at the canonical root, with the same static
    # SEO content and asset paths as existing wallet.html links.
    shutil.copy2(output / "wallet.html", output / "index.html")
    package_licenses(ROOT, output)
    print(f"GitHub Pages artifact: {output}")


if __name__ == "__main__":
    main()
