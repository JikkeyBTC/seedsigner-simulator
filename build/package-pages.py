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
    (output / "index.html").write_text('''<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="직키 JikKey의 SeedSigner·ShieldSigner 웹 시뮬레이터. 설치 없이 브라우저에서 기기 화면과 지갑 기능을 안전하게 체험해 보세요.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://jikkeybtc.github.io/seedsigner-simulator/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="직키 JikKey">
<meta property="og:locale" content="ko_KR">
<meta property="og:title" content="직키 JikKey · SeedSigner·ShieldSigner 시뮬레이터">
<meta property="og:description" content="브라우저에서 SeedSigner와 ShieldSigner를 체험하는 직키 공식 웹 시뮬레이터입니다.">
<meta property="og:url" content="https://jikkeybtc.github.io/seedsigner-simulator/">
<meta property="og:image" content="https://jikkeybtc.github.io/seedsigner-simulator/jikkey-card-photo.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="직키 JikKey · SeedSigner·ShieldSigner 시뮬레이터">
<meta name="twitter:description" content="설치 없이 브라우저에서 SeedSigner와 ShieldSigner를 체험해 보세요.">
<title>직키 JikKey · SeedSigner·ShieldSigner 시뮬레이터</title>
<link rel="icon" href="favicon.ico" sizes="16x16 32x32 48x48 64x64">
<link rel="icon" href="jikkey-favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="apple-touch-icon.png?v=pixel-j" sizes="180x180">
<meta name="theme-color" content="#ff8508">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "직키 JikKey SeedSigner·ShieldSigner 시뮬레이터",
  "alternateName": ["JikKey Simulator", "직키 시뮬레이터", "SeedSigner 시뮬레이터", "ShieldSigner 시뮬레이터"],
  "url": "https://jikkeybtc.github.io/seedsigner-simulator/",
  "description": "직키 JikKey가 제공하는 SeedSigner 및 ShieldSigner 웹 시뮬레이터입니다.",
  "applicationCategory": "EducationalApplication",
  "operatingSystem": "Web",
  "inLanguage": "ko",
  "isAccessibleForFree": true,
  "publisher": {"@type": "Organization", "name": "JikKey", "url": "https://jikkey.com"}
}
</script>
<style>
  :root { color-scheme: light; --orange: #ff8508; --ink: #17120e; --muted: #6d6259; --card: #fffaf4; }
  * { box-sizing: border-box; }
  body { margin: 0; color: var(--ink); background: #fff; font: 16px/1.7 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
  main { max-width: 52rem; margin: 0 auto; padding: 3.5rem 1.25rem 4rem; }
  .brand { display: flex; align-items: center; gap: .7rem; margin-bottom: 2.5rem; }
  .brand img { width: auto; height: 2rem; }
  .brand span { color: var(--muted); font-size: .9rem; font-weight: 600; }
  h1 { max-width: 40rem; margin: 0 0 1rem; font-size: clamp(2rem, 5vw, 3.3rem); line-height: 1.15; letter-spacing: -.03em; }
  .lead { max-width: 42rem; color: var(--muted); font-size: 1.12rem; margin: 0 0 1.6rem; }
  .cta { display: inline-block; color: #1c1208; background: var(--orange); border-radius: 999px; padding: .8rem 1.35rem; font-weight: 750; text-decoration: none; box-shadow: 0 8px 22px #ff85083d; }
  .cta:hover { filter: brightness(.96); }
  .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: .8rem; margin: 3rem 0 2rem; }
  .card { padding: 1rem; border: 1px solid #eee3d8; border-radius: 14px; background: var(--card); }
  .card strong { display: block; margin-bottom: .2rem; }
  .card span { color: var(--muted); font-size: .9rem; }
  .note { border-top: 1px solid #eee3d8; padding-top: 1.4rem; color: var(--muted); font-size: .92rem; }
  footer { margin-top: 2.5rem; color: var(--muted); font-size: .86rem; }
  footer a { color: inherit; }
  @media (max-width: 38rem) { main { padding-top: 2.25rem; } .grid { grid-template-columns: 1fr; } }
</style>
</head>
<body><main>
<div class="brand"><img src="jikkey-logo.svg" alt="JikKey"><span>직키 시뮬레이터</span></div>
<h1>직키 JikKey<br>SeedSigner·ShieldSigner 시뮬레이터</h1>
<p class="lead">실제 SeedSigner 화면과 ShieldSigner 스마트카드 기능을 설치 없이 브라우저에서 체험해 보세요. PC와 휴대폰 모두 사용할 수 있습니다.</p>
<a class="cta" href="wallet.html?firmware=smartcard&amp;wallet=1">시뮬레이터 시작하기</a>
<section class="grid" aria-label="지원 기능">
  <div class="card"><strong>SeedSigner</strong><span>오픈소스 비트코인 서명 장치 화면 체험</span></div>
  <div class="card"><strong>ShieldSigner</strong><span>SeedKeeper·스마트카드 메뉴 포함</span></div>
  <div class="card"><strong>JikKey</strong><span>직키의 한국어 안내와 반응형 화면</span></div>
</section>
<p class="note">이 웹사이트는 학습과 UI 확인을 위한 시뮬레이터입니다. 실제 지갑이나 보안 장치를 대신하지 않으며, 실제로 사용하는 시드 문구와 개인키를 입력하지 마세요.</p>
<footer><a href="licenses/">오픈소스 라이선스</a> · <a href="https://github.com/JikkeyBTC/seedsigner-simulator">소스 코드</a></footer>
</main></body></html>
''', encoding="utf-8")
    package_licenses(ROOT, output)
    print(f"GitHub Pages artifact: {output}")


if __name__ == "__main__":
    main()
