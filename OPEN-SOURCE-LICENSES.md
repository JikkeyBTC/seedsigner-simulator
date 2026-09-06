# 오픈소스 라이선스

이 프로젝트는 [BitsagaRob의 SeedSigner simulator](https://github.com/bitsagarob/seedsigner-simulator)를
포크해 직키가 수정한 시뮬레이터입니다. 원본의 저작권과 라이선스 고지를 유지합니다.
직키 수정본에는 기기 외형, 웹 페이지의 한국어·영어 전환, 렌더링, 모바일 조작,
카드 표시, ShieldSigner B12 선택과 GitHub Pages 배포 구성이 포함됩니다.

- 원본 시뮬레이터: **Copyright (c) 2026 BitsagaRob**, [MIT 전문](LICENSE)
- SeedSigner 및 ShieldSigner의 기반 펌웨어: **Copyright (c) 2021 SeedSigner**, MIT
- 직키 수정본: [소스 저장소](https://github.com/JikkeyBTC/seedsigner-simulator/tree/sandbox/0906_work)
- 실제 배포 버전: [오픈소스 라이선스 페이지](https://jikkeybtc.github.io/seedsigner-simulator/licenses/)
- 전체 고지: [고지 전문 TXT](https://jikkeybtc.github.io/seedsigner-simulator/licenses/THIRD-PARTY-NOTICES.txt)
- 버전·커밋·소스·고지 파일: [구성요소 JSON](https://jikkeybtc.github.io/seedsigner-simulator/licenses/components.json)
- 배포에 사용된 직키 수정본 소스: [소스 ZIP](https://jikkeybtc.github.io/seedsigner-simulator/licenses/simulator-source.zip)

MIT는 고지를 유지하는 조건으로 수정·재배포·상업적 이용을 허용합니다.
함께 배포되는 라이브러리와 폰트에는 각각의 라이선스가 적용됩니다.
각 라이선스의 원문이 이 설명보다 우선합니다. 원본 프로젝트의 상표나 로고에 대한
권리, 제휴·보증을 표시할 권리를 이 문서가 부여하는 것은 아닙니다.

## 포함된 코드와 라이선스

| 구성요소 | 적용 조건과 소스 위치 |
| --- | --- |
| 시뮬레이터와 하드웨어 대체 모듈 | MIT. `LICENSE`를 유지합니다. `licenses/simulator-source.zip`에 배포에 사용한 소스와 빌드 스크립트가 있습니다. |
| ShieldSigner B12 / SeedSigner 0.8.7 | MIT. 선택한 버전·커밋은 `UPSTREAM`과 `wallet-*.build-info.json`에 기록됩니다. `wallet-smartcard.zip` / `wallet-stock.zip`에 실제 Python 소스와 고지가 들어 있습니다. |
| PyGP / pysatochip | LGPL-3.0. `wallet-smartcard.zip` 안의 `pygp/`와 `pysatochip/`이 실제 실행되는 라이브러리 소스입니다. 수정·교체 방법은 아래에 설명합니다. |
| Pyodide / hiwire / certifi | MPL-2.0 적용 소스와 해당 수정에는 MPL 조건이 적용됩니다. Pyodide는 0.26.4 태그의 소스·패치·빌드 레시피를 사용합니다. Pyodide의 npm 메타데이터에는 Apache-2.0도 표시되어 있어 두 고지를 보관합니다. |
| jsQR | Apache-2.0. 배포한 1.4.0 npm 아카이브의 라이선스 전문을 포함합니다. |
| 그 밖의 Python·C 라이브러리와 폰트 | 배포한 ZIP·wheel에서 고지를 추출하고, 누락된 런타임·폰트의 원문을 `licenses/vendor/`에서 보충합니다. 전체 버전과 출처는 `licenses/components.json`에 있습니다. |

PyGP와 pysatochip 및 그 사용에는 LGPL-3.0이 적용됩니다.
[LGPL-3.0 전문](licenses/vendor/LGPL-3.0.txt)과
[GPL-3.0 전문](licenses/vendor/GPL-3.0.txt)을 함께 제공합니다.
수령인은 라이브러리를 수정하거나 호환되는 수정본으로 교체할 수 있습니다.
그러한 수정을 디버깅하기 위한 역공학도 제한하지 않습니다.
LGPL 라이브러리를 수정해 배포한다면 수정된 해당 소스와 고지를 함께 제공하세요.
이 고지는 별도로 작성된 애플리케이션 전체를 LGPL로 다시 허가한다는 뜻은 아닙니다.

MPL 적용 소스는 다음에서 받을 수 있습니다. 배포한 바이너리에 사용된 버전을
지정하며, 변경 없이 재배포하더라도 해당 소스를 얻는 방법을 안내합니다.

- [Pyodide 0.26.4 전체 소스·패치·패키지 레시피](https://github.com/pyodide/pyodide/tree/0.26.4),
  [소스 아카이브](https://github.com/pyodide/pyodide/archive/refs/tags/0.26.4.tar.gz),
  [MPL 전문](licenses/vendor/Pyodide-LICENSE.txt)
- [hiwire 고정 커밋의 소스](https://github.com/hoodmane/hiwire/tree/49f3450e34f3f50d4b8296e782dc321bb2e3264e),
  [소스 아카이브](https://github.com/hoodmane/hiwire/archive/49f3450e34f3f50d4b8296e782dc321bb2e3264e.tar.gz),
  [MPL 전문](licenses/vendor/hiwire-LICENSE.txt)
- certifi 2025.7.14: 배포한 `wallet-smartcard.zip`의 `certifi/`와
  `licenses/certifi.LICENSE`, [원본 배포 파일](https://pypi.org/project/certifi/2025.7.14/#files)

## 런타임·폰트 고지

This software is based in part on the work of the Independent JPEG Group.

Portions of this software are copyright © The FreeType Project (www.freetype.org).
All rights reserved. This distribution selects the FreeType License (FTL) option.

This product includes software developed by the OpenSSL Project for use in the
OpenSSL Toolkit (https://www.openssl.org/).
This product includes cryptographic software written by Eric Young (eay@cryptsoft.com).
This product includes software written by Tim Hudson (tjh@cryptsoft.com).

CPython, Emscripten의 런타임, libffi, hiwire, OpenSSL, 압축·이미지·폰트 라이브러리의
전문과 출처도 포함합니다. OpenSSL 파일명과 lock 파일은 `1.1.1n`으로 표시되지만,
Pyodide 0.26.4 빌드 레시피가 가져오는 소스는 **1.1.1w**입니다.

Font Awesome Free의 OTF 폰트에는 OFL-1.1이 적용됩니다. Inconsolata, Noto Sans
Devanagari, PlemolJP에도 OFL 고지를 포함하며, 배포한 Open Sans 1.10에는 해당 폰트의
메타데이터에 명시된 Apache-2.0 고지를 포함합니다. 각 폰트의 원래 저작권·버전·라이선스
메타데이터와 SHA-256은 배포 시 `licenses/FONT-NOTICES.txt`에 기록됩니다.
폰트 고유의 고지와 Reserved Font Name 조건을 유지하세요.

## 같은 버전으로 재빌드하기

Linux 또는 WSL에서 Bash, Git, curl, Python 3.12 이상과 SHA-256 도구를 준비합니다.
배포에 사용한 커밋은 `licenses/components.json`의 `simulator.commit`입니다.
`modified_worktree`가 `true`인 로컬 패키지는 커밋 이후의 변경도 포함하므로
그 패키지에 동봉된 소스 ZIP을 사용하세요.

```sh
git clone https://github.com/JikkeyBTC/seedsigner-simulator.git
cd seedsigner-simulator
git checkout <components.json에 기록된 커밋>
bash build/fetch-assets.sh
bash build/build-wallet-zip.sh smartcard
bash build/build-wallet-zip.sh stock
python3 build/package-pages.py --output build/public
python3 build/check-license-bundle.py build/public
python3 test/serve.py --port 8770 build/public
```

브라우저에서 `http://127.0.0.1:8770/`을 엽니다. `build/public/` 전체가
고지·소스·런타임을 포함한 배포물입니다. 출력 경로는 새 디렉터리이거나 비어 있어야 합니다.
Git 저장소 대신 소스 ZIP을 풀어도 같은 명령으로 빌드할 수 있습니다.
소스 ZIP의 `SOURCE-SNAPSHOT.json`에는 포함된 파일의 SHA-256과 기준 커밋이 들어 있습니다.

정확한 아티팩트 URL과 체크섬은 `build/build-wallet-zip.sh`,
`build/fetch-assets.sh`, `UPSTREAM`, `pyodide/pyodide-lock.json`에 기록되어 있습니다.
`sha256sum build/out/wallet-*.zip`으로 배포 파일과 비교할 수 있습니다.
압축 라이브러리 차이로 ZIP 바이트가 다를 때는 `wallet-*.zip.manifest`도 비교하세요.

## LGPL 라이브러리 수정·교체하기

라이브러리는 암호화되거나 서명으로 교체가 잠긴 바이너리가 아니라 Python 소스입니다.
다음 방법으로 자신의 라이브러리 소스를 사용해 재빌드할 수 있습니다.

1. `licenses/components.json`의 PyGP 또는 pysatochip 소스 주소에서 해당 커밋을 받습니다.
2. 라이브러리를 수정하고 자신의 저장소에 커밋합니다. 기존 라이브러리 고지를 유지합니다.
3. 시뮬레이터의 `build/build-wallet-zip.sh`에서 해당 `git|pygp|...` 또는
   `git|pysatochip|...` 행의 저장소 URL을 자신의 URL로 바꿉니다. 그 행의 버전 필드와
   무결성 필드 두 곳 모두 새 커밋의 전체 SHA로 바꿉니다. 모듈명·배포명·하위 경로는 유지합니다.
4. `bash build/build-wallet-zip.sh smartcard`로 다시 빌드합니다.
5. 위의 패키징·로컬 서버 명령으로 실행합니다. 라이브러리 사용처와 호환되는 인터페이스를 유지해야 합니다.

수정본은 공개된 원본 ZIP과 해시가 달라져 기술 정보에 다른 빌드로 표시됩니다.
이 해시 비교는 안내용이며, 수정한 라이브러리의 실행을 차단하지 않습니다.
웹 코드·대체 모듈을 수정했다면 패키징 전에 `bash build/update-checksums.sh`도 실행합니다.
Git 작업 디렉터리에서 새 소스 파일을 추가했다면 먼저 `git add`로 포함할 파일을 명시하세요.
소스 아카이브에는 Git이 추적하는 파일만 들어가며, 개인 캐시나 로컬 설정은 수집하지 않습니다.

이 시뮬레이터의 패키징은 Pyodide를 새로 컴파일하지 않고 고정된 0.26.4 아티팩트를 사용합니다.
Pyodide 자체를 수정하려면 [0.26.4의 빌드 문서](https://pyodide.org/en/0.26.4/development/building-from-sources.html)와
동일 태그의 `Makefile`, `Makefile.envs`, `cpython/`, `packages/` 레시피를 사용하세요.
CPython 3.12.1과 Emscripten 3.1.58을 포함한 입력·패치는 그 소스에 명시되어 있습니다.
런타임 버전을 바꾸면 `licenses/supplemental.json`의 고정 버전·출처·고지도 함께 갱신해야 합니다.

## 배포할 때 함께 보관할 파일

`build/package-pages.py`는 다음을 자동으로 포함합니다.

- 루트 `LICENSE`, `THIRD-PARTY.md`, `OPEN-SOURCE-LICENSES.md`, `UPSTREAM`
- `licenses/index.html`: 사용 버전·소스·라이선스를 찾는 공개 페이지
- `licenses/THIRD-PARTY-NOTICES.txt`: 수집한 고지 전문
- `licenses/components.json`: 실제 빌드 입력에서 만든 구성요소 목록
- `licenses/supplemental.json`: 보충 고지의 원문 URL·SHA-256
- `licenses/simulator-source.zip`: 직키 수정본의 실제 소스와 빌드·검증 스크립트
- `licenses/build/`, `licenses/FONT-NOTICES.txt`, `licenses/files.json`
- `wallet-*.zip`, `wallet-*.zip.manifest`, `wallet-*.build-info.json`, `pyodide/`

위 파일들은 함께 배포하세요. `licenses/`만 별도로 제공하고 실제 소스·펌웨어를
빼거나, 원본 저장소 링크만 남기고 배포한 수정본 소스를 누락하지 않도록 합니다.
현재 이 목록의 범위는 ShieldSigner·SeedSigner 웹 시뮬레이터이며, 별도로 빌드하는
DOOM 엔진·게임 데이터와 Java Card applet 바이너리는 포함하지 않습니다.
