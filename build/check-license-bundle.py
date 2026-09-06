"""Check the actual static distribution without starting or operating a device."""

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import zipfile


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.extend(v for k, v in attrs if k == "href")


def check(root):
    root = root.resolve()
    base = root / "licenses"
    assert not (root / "doom.js").exists() and not (root / "doom.wasm").exists()
    assert not list(root.glob("*.wad")), "DOOM data is outside this wallet-only license bundle"
    required = [root / name for name in ("LICENSE", "THIRD-PARTY.md", "OPEN-SOURCE-LICENSES.md", "UPSTREAM")]
    required += [base / name for name in ("index.html", "components.json", "files.json", "supplemental.json",
                 "THIRD-PARTY-NOTICES.txt", "FONT-NOTICES.txt", "simulator-source.zip",
                 "vendor/GPL-3.0.txt", "vendor/LGPL-3.0.txt", "vendor/Pyodide-LICENSE.txt")]
    for path in required:
        if not path.is_file() or not path.stat().st_size:
            raise ValueError(f"missing or empty distributed file: {path.relative_to(root)}")
    assert "Copyright (c) 2026 BitsagaRob" in (root / "LICENSE").read_text(encoding="utf-8")
    gpl = (base / "vendor/GPL-3.0.txt").read_text(encoding="utf-8")
    assert "GNU GENERAL PUBLIC LICENSE" in gpl and len(gpl) > 30000
    assert "GNU LESSER GENERAL PUBLIC LICENSE" in (base / "vendor/LGPL-3.0.txt").read_text(encoding="utf-8")

    manifest = json.loads((base / "files.json").read_text(encoding="utf-8"))
    for name, expected in manifest.items():
        path = (base / name).resolve()
        if not path.is_relative_to(base) or not path.is_file():
            raise ValueError(f"invalid notice manifest path: {name}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"distributed file checksum mismatch: {name}")
    index = Links()
    index.feed((base / "index.html").read_text(encoding="utf-8"))
    info = json.loads((base / "components.json").read_text(encoding="utf-8"))
    for item in info["components"]:
        assert item["name"] and item["version"] and item["source"] and item["notices"], item
        index.links.extend(item["notices"])
        if item.get("source_archive"):
            index.links.append(item["source_archive"])
    for url in index.links:
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc:
            assert parsed.scheme == "https", url
            continue
        target = (base / unquote(parsed.path)).resolve()
        if not target.is_relative_to(root):
            raise ValueError(f"link escapes the distribution: {url}")
        if target.is_dir():
            target /= "index.html"
        if not target.is_file():
            raise ValueError(f"broken local license/source link: {url}")
    # Check repository-relative links in the document shipped in both places.
    doc = (root / "OPEN-SOURCE-LICENSES.md").read_text(encoding="utf-8")
    for url in re.findall(r"\]\(([^)]+)\)", doc):
        if not urlsplit(url).scheme and not url.startswith("#"):
            assert (root / unquote(urlsplit(url).path)).is_file(), url
    with zipfile.ZipFile(base / "simulator-source.zip") as archive:
        snapshot = json.loads(archive.read("SOURCE-SNAPSHOT.json"))
        for name in ("LICENSE", "README.md", "OPEN-SOURCE-LICENSES.md", "UPSTREAM",
                     "build/build-wallet-zip.sh", "build/package-pages.py", "build/package_licenses.py",
                     "build/check-license-bundle.py", "test/serve.py", "licenses/vendor/GPL-3.0.txt"):
            assert name in snapshot["files"], f"missing rebuild source: {name}"
        for name, expected in snapshot["files"].items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == expected, name
        assert archive.read("src/web/wallet.html") == (root / "wallet.html").read_bytes()
        assert archive.read("src/web/jikkey-i18n.js") == (root / "jikkey-i18n.js").read_bytes()
    for firmware in ("smartcard", "stock"):
        with zipfile.ZipFile(root / f"wallet-{firmware}.zip") as archive:
            assert archive.read("licenses/SeedSigner.LICENSE") == (base / firmware / "licenses/SeedSigner.LICENSE").read_bytes()
            if firmware == "smartcard":
                assert "pygp/__init__.py" in archive.namelist()
                assert "pysatochip/__init__.py" in archive.namelist()
    print(f"License bundle OK: {len(info['components'])} component records; {len(manifest)} file hashes; local links and source archive verified.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        check(args.directory)
    except (AssertionError, KeyError, ValueError, OSError, zipfile.BadZipFile) as exc:
        parser.exit(1, f"license bundle check failed: {exc}\n")
