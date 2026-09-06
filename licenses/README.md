# 오픈소스 라이선스 자료

[이용 조건·버전·소스·재빌드 방법](../OPEN-SOURCE-LICENSES.md) ·
[배포본의 라이선스 페이지](https://jikkeybtc.github.io/seedsigner-simulator/licenses/)

`vendor/`는 펌웨어 ZIP이나 Pyodide wheel에 없는 고지 전문을 보충합니다.
`supplemental.json`에는 각 원문의 출처, 대상 버전과 커밋, 소스 아카이브,
고지 파일의 SHA-256이 기록되어 있습니다. 원문은 UTF-8/LF로 보관합니다.

`build/package_licenses.py`는 실제 배포하는 펌웨어·wheel 안의 고지를 추출하고,
이 보충 파일들과 함께 `build/pages/licenses/`에 모읍니다. 생성한 목록은
`components.json`, 모든 고지의 통합본은 `THIRD-PARTY-NOTICES.txt`입니다.
정적 링크 목록을 최신 버전으로 추측해 바꾸지 말고, 빌드 입력과 함께 갱신하세요.

이 디렉터리의 라이선스 전문에는 각 원문 자체의 조건이 적용됩니다.
저장소 루트의 MIT 라이선스가 제삼자 코드나 폰트의 라이선스를 대체하지 않습니다.
