"""Collect notices and source provenance from the files actually being served.

No network access and no changes to firmware/runtime archives. Missing notices,
changed supplemental texts and unknown dependency pins stop the Pages build.
"""

import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import zipfile


REPOSITORY = "https://github.com/JikkeyBTC/seedsigner-simulator"
UPSTREAM = "https://github.com/bitsagarob/seedsigner-simulator"
DOCS = ("LICENSE", "THIRD-PARTY.md", "OPEN-SOURCE-LICENSES.md", "UPSTREAM")
PYTHON_LICENSES = {
    "base58": "MIT", "certifi": "MPL-2.0", "ecdsa": "MIT", "embit": "MIT",
    "mnemonic": "MIT", "ndeflib": "ISC", "pyOpenSSL": "Apache-2.0",
    "pyaes": "MIT", "pyasn1": "BSD-2-Clause", "qrcode": "BSD-3-Clause + MIT",
    "shamir-mnemonic": "MIT", "six": "MIT", "typing_extensions": "PSF-2.0",
    "PGPy-3rdIteration-fork": "BSD-3-Clause", "PyGP-3rdIteration-fork": "LGPL-3.0",
    "pysatochip-3rdIteration": "LGPL-3.0", "specter-card": "MIT", "urtypes": "MIT",
}
RUNTIME_LICENSES = {
    "pillow": "HPND", "pycryptodome": "BSD-2-Clause + public domain",
    "cryptography": "Apache-2.0 OR BSD-3-Clause", "cffi": "MIT",
    "pycparser": "BSD-3-Clause", "six": "MIT", "openssl": "OpenSSL AND SSLeay",
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def notice_name(name):
    return bool(re.search(r"(^|[._-])(licen[cs]e|copying|copyright|notice)([._-]|$)", Path(name).name, re.I))


def extract_notices(archive, target, base, prefix=None):
    """Keep original paths and bytes; never extract arbitrary archive members."""
    results = []
    for name in sorted(archive.namelist()):
        if name.endswith("/") or not notice_name(name):
            continue
        if prefix and not name.startswith(prefix):
            continue
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts or "\\" in name:
            raise ValueError(f"unsafe notice path: {name}")
        dest = target / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        data = archive.read(name)
        if not data.strip():
            raise ValueError(f"empty notice: {name}")
        dest.write_bytes(data)
        results.append(dest.relative_to(base).as_posix())
    return results


def font_names(data):
    """Read copyright/version/license SFNT name records without a font dependency."""
    names = {0: [], 5: [], 13: [], 14: []}
    for i in range(struct.unpack_from(">H", data, 4)[0]):
        tag, _, offset, _ = struct.unpack_from(">4sIII", data, 12 + i * 16)
        if tag != b"name":
            continue
        _, count, start = struct.unpack_from(">HHH", data, offset)
        for j in range(count):
            platform, _, _, ident, length, index = struct.unpack_from(">HHHHHH", data, offset + 6 + j * 12)
            if ident not in names:
                continue
            value = data[offset + start + index:offset + start + index + length]
            value = value.decode("utf-16-be" if platform in (0, 3) else "latin1", errors="replace")
            if value not in names[ident]:
                names[ident].append(value)
    return names


def source_snapshot(root, target):
    """Archive tracked source bytes, including staged additions, never local caches."""
    if (root / ".git").exists():
        def git(*args):
            return subprocess.check_output(["git", "-C", str(root), *args])
        paths = sorted(git("ls-files", "-z").decode("utf-8").strip("\0").split("\0"))
        commit = git("rev-parse", "HEAD").decode().strip()
        modified = bool(git("status", "--porcelain", "--untracked-files=no").strip())
    else:
        previous = json.loads((root / "SOURCE-SNAPSHOT.json").read_text(encoding="utf-8"))
        paths, commit = sorted(previous["files"]), previous["commit"]
        modified = previous["modified_worktree"] or any(
            not (root / p).is_file() or digest((root / p).read_bytes()) != h
            for p, h in previous["files"].items())
    # A newly added notice must not silently disappear from the source archive.
    required = ["build/package_licenses.py", "OPEN-SOURCE-LICENSES.md", "licenses/supplemental.json"]
    required += [p.relative_to(root).as_posix() for p in (root / "licenses").rglob("*") if p.is_file()]
    if set(required) - set(paths):
        raise ValueError("stage the new license files before packaging a source snapshot")
    info = {"repository": REPOSITORY, "commit": commit, "modified_worktree": modified, "files": {}}
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in paths:
            source = root / path
            if not source.is_file():
                continue  # tracked file deliberately deleted in a local checkout
            if source.is_symlink():
                raise ValueError(f"source snapshot does not follow symlinks: {path}")
            data = source.read_bytes()
            info["files"][path] = digest(data)
            entry = zipfile.ZipInfo(path, (1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data)
        entry = zipfile.ZipInfo("SOURCE-SNAPSHOT.json", (1980, 1, 1, 0, 0, 0))
        archive.writestr(entry, json.dumps(info, ensure_ascii=False, indent=2) + "\n")
    return info


def package_licenses(root, output):
    base = output / "licenses"
    base.mkdir()
    shutil.copytree(root / "licenses", base, dirs_exist_ok=True)
    for name in DOCS:
        shutil.copy2(root / name, output / name)
    (output / "docs").mkdir(exist_ok=True)
    shutil.copy2(root / "docs/SELF-HOSTING.md", output / "docs/SELF-HOSTING.md")
    for name in ("build-wallet-zip.sh", "fetch-assets.sh", "update-checksums.sh", "checksums.txt", "package-pages.py", "package_licenses.py", "check-license-bundle.py"):
        dest = base / "build" / name
        dest.parent.mkdir(exist_ok=True)
        shutil.copy2(root / "build" / name, dest)

    components = json.loads((base / "supplemental.json").read_text(encoding="utf-8"))
    for item in components:
        for notice in item["notices"]:
            if digest((base / notice["path"]).read_bytes()) != notice["sha256"]:
                raise ValueError(f"supplemental notice checksum mismatch: {notice['path']}")
        item["notices"] = [n["path"] for n in item["notices"]]
    # Exact upstream pins/artifact URLs already maintained by the wallet builder.
    pins = {}
    for line in (root / "build/build-wallet-zip.sh").read_text(encoding="utf-8").splitlines():
        if line.startswith(("pypi|", "git|")):
            kind, module, dist, version, url, integrity, subpath = line.split("|")
            pins[(dist, version)] = (kind, url, integrity)

    font_notices = []
    archive_notices = set()
    for firmware in ("smartcard", "stock"):
        info = json.loads((output / f"wallet-{firmware}.build-info.json").read_text(encoding="utf-8"))
        pin = info["upstream"]
        source = pin["repo"].removesuffix(".git") + "/tree/" + pin["commit"]
        with zipfile.ZipFile(output / f"wallet-{firmware}.zip") as archive:
            notices = extract_notices(archive, base / firmware, base)
            archive_notices.update(notices)
            seed_notice = f"{firmware}/licenses/SeedSigner.LICENSE"
            if seed_notice not in notices:
                raise ValueError(f"missing SeedSigner notice in {firmware}")
            components.append(dict(name="ShieldSigner" if firmware == "smartcard" else "SeedSigner",
                version=pin["tag"], commit=pin["commit"], license="MIT", scope=firmware,
                source=source, source_archive=f"../wallet-{firmware}.zip", notices=[seed_notice]))
            for dep in info["dependencies"]:
                kind, url, integrity = pins[(dep["name"], dep["version"])]
                notice = f"{firmware}/licenses/{dep['name']}.LICENSE"
                if notice not in notices:
                    raise ValueError(f"missing dependency notice: {notice}")
                components.append(dict(name=dep["name"], version=dep["version"], scope=firmware,
                    license=PYTHON_LICENSES[dep["name"]], notices=[notice], artifact=url,
                    artifact_integrity=integrity,
                    source=url.removesuffix(".git") + "/tree/" + integrity if kind == "git"
                    else f"https://pypi.org/project/{dep['name']}/{dep['version']}/#files",
                    source_archive=f"../wallet-{firmware}.zip"))
            for name in sorted(archive.namelist()):
                if not name.endswith((".ttf", ".otf")):
                    continue
                data = archive.read(name)
                metadata = font_names(data)
                filename = Path(name).name
                if filename.startswith("OpenSans"):
                    license, texts = "Apache-2.0", ["vendor/jsQR-LICENSE.txt"]
                elif filename == "seedsigner-icons.otf":
                    license, texts = "MIT (SeedSigner resources)", [seed_notice]
                else:
                    license, texts = "OFL-1.1", ["vendor/OFL-1.1.txt"]
                    if filename.startswith("Plemol"):
                        texts += ["vendor/PlemolJP-LICENSE.txt", "vendor/PlemolJP-IBM-Plex-LICENSE.txt", "vendor/PlemolJP-NerdFonts-LICENSE.txt"]
                    if filename.startswith("Font_Awesome"):
                        texts += ["vendor/Font-Awesome-LICENSE.txt"]
                components.append(dict(name=filename, version="; ".join(metadata[5]) or "upstream font",
                    license=license, scope=firmware + " fonts", source=source + "/" + name.replace("seedsigner/", "src/seedsigner/", 1),
                    source_archive=f"../wallet-{firmware}.zip", sha256=digest(data), notices=texts + ["FONT-NOTICES.txt"]))
                font_notices.append(f"{firmware}: {name}\nSHA256: {digest(data)}\nSource: {source}\n" +
                    "\n".join(f"{label}: {'; '.join(metadata[key])}" for key, label in [(0, "Copyright"), (5, "Version"), (13, "License"), (14, "License URL")]) + "\n")
    (base / "FONT-NOTICES.txt").write_text("\n".join(font_notices), encoding="utf-8")

    lock = json.loads((output / "pyodide/pyodide-lock.json").read_text(encoding="utf-8"))
    if lock["info"]["version"] != "0.26.4":
        raise ValueError("update supplemental runtime notices for the new Pyodide version")
    for key, package in sorted(lock["packages"].items()):
        artifact = output / "pyodide" / package["file_name"]
        if not artifact.is_file():
            continue
        if digest(artifact.read_bytes()) != package["sha256"]:
            raise ValueError(f"runtime package checksum mismatch: {artifact.name}")
        with zipfile.ZipFile(artifact) as archive:
            notices = extract_notices(archive, base / "runtime" / key, base)
        if key == "openssl":
            notices = ["vendor/OpenSSL-LICENSE.txt"]
        if not notices:
            raise ValueError(f"missing runtime notices for {key}")
        archive_notices.update(notices)
        recipe_name = "Pillow" if key == "pillow" else key
        components.append(dict(name=package["name"], version=package["version"], scope="Pyodide package",
            license=RUNTIME_LICENSES[key], notices=notices,
            source=f"https://github.com/pyodide/pyodide/tree/0.26.4/packages/{recipe_name}",
            source_archive="https://github.com/pyodide/pyodide/archive/refs/tags/0.26.4.tar.gz",
            artifact=f"../pyodide/{artifact.name}", artifact_integrity=package["sha256"],
            note="Artifact label is 1.1.1n; recipe builds OpenSSL 1.1.1w." if key == "openssl" else ""))

    snapshot = source_snapshot(root, base / "simulator-source.zip")
    components.insert(0, dict(name="JikKey SeedSigner simulator (BitsagaRob fork)",
        version=snapshot["commit"] + (" + working tree changes" if snapshot["modified_worktree"] else ""),
        license="MIT", scope="web and hardware shims", source=REPOSITORY + "/tree/" + snapshot["commit"],
        source_archive="simulator-source.zip", notices=["../LICENSE"], upstream=UPSTREAM))
    write_json(base / "components.json", {"simulator": {k: v for k, v in snapshot.items() if k != "files"}, "components": components})

    # A single text download includes notices from the firmware, wheels and supplements.
    texts = {"../LICENSE"} | archive_notices
    texts.update(n for item in components for n in item["notices"])
    combined = []
    for name in sorted(texts):
        data = (base / name).read_bytes()
        combined.append(f"{'=' * 72}\n{name}\n{'=' * 72}\n" + data.decode("utf-8", errors="replace") + "\n")
    (base / "THIRD-PARTY-NOTICES.txt").write_text("\n".join(combined), encoding="utf-8")
    rows = []
    def link(url, label):
        return f'<a href="{html.escape(url, quote=True)}">{html.escape(label)}</a>'
    for item in components:
        links = [link(n, Path(n).name) for n in item["notices"]]
        source_links = [link(item["source"], "소스 / Source")]
        if item.get("source_archive"):
            source_links.append(link(item["source_archive"], "소스 다운로드 / Download"))
        rows.append("<tr>" + "".join(f"<td>{html.escape(str(item.get(k, '')))}</td>" for k in ("name", "version", "license", "scope")) +
                    f"<td>{'<br>'.join(source_links)}</td><td>{'<br>'.join(links)}</td></tr>")
    (base / "index.html").write_text('''<!doctype html>
<html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>오픈소스 라이선스 · JikKey</title>
<style>body{font:16px/1.7 system-ui,sans-serif;color:#242424;background:#fff;margin:0 auto;padding:32px 20px;max-width:1200px}a{color:#8a3700}h1{line-height:1.25}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:12px;text-align:left;vertical-align:top;border-bottom:1px solid #ddd;overflow-wrap:anywhere}th{background:#f5f5f5}.table{overflow:auto}td:nth-child(2){max-width:230px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f6f6f6;padding:16px}nav a{display:inline-block;margin:0 16px 8px 0}</style>
<body><a href="../wallet.html?firmware=smartcard&amp;wallet=1">← 시뮬레이터</a>
<h1>오픈소스 라이선스</h1><p>Open-source licenses, notices and corresponding source</p>
<p>이 시뮬레이터는 BitsagaRob의 SeedSigner simulator를 바탕으로 직키가 수정한 프로젝트입니다.
원저작권 고지는 유지되며, 포함된 각 구성요소에는 아래의 개별 라이선스가 적용됩니다.</p>
<p>Copyright (c) 2026 BitsagaRob · Copyright (c) 2021 SeedSigner</p>
<p>PyGP와 pysatochip 및 그 사용에는 LGPL-3.0이 적용됩니다. GPL·LGPL 전문과 해당 Python 소스를 함께 제공합니다.
사용자는 라이브러리를 수정·교체할 수 있고, 그 수정을 디버깅하기 위한 역공학을 제한하지 않습니다.
Pyodide·hiwire·certifi의 MPL 적용 소스도 아래에서 받을 수 있습니다.</p>
<p>This software is based in part on the work of the Independent JPEG Group.
Portions of this software are copyright © The FreeType Project (www.freetype.org). All rights reserved.
This product includes software developed by the OpenSSL Project for use in the OpenSSL Toolkit
(https://www.openssl.org/), and cryptographic software written by Eric Young (eay@cryptsoft.com).
This product includes software written by Tim Hudson (tjh@cryptsoft.com).</p>
<nav><a href="THIRD-PARTY-NOTICES.txt">고지 전문</a><a href="../OPEN-SOURCE-LICENSES.md">이용 조건·재빌드 방법</a>
<a href="components.json">사용 버전·소스 목록 JSON</a><a href="simulator-source.zip">직키 수정본 소스 ZIP</a>
<a href="../THIRD-PARTY.md">구성요소 설명</a></nav>
<p>펌웨어 다운로드에는 해당 펌웨어와 LGPL 라이브러리의 Python 소스가 들어 있습니다.
동일한 디렉터리에 제공되는 고지와 재빌드 문서를 함께 보관하세요.</p>
<div class="table"><table><thead><tr><th>구성요소</th><th>버전·커밋</th><th>라이선스</th><th>사용 위치</th><th>소스</th><th>고지 전문</th></tr></thead><tbody>
''' + "\n".join(rows) + "</tbody></table></div></body></html>\n", encoding="utf-8")
    write_json(base / "files.json", {p.relative_to(base).as_posix(): digest(p.read_bytes())
                                   for p in sorted(base.rglob("*")) if p.is_file()})
    print(f"License bundle: {len(components)} component records, {len(texts)} notice texts")
