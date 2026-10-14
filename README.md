# 거리 · 운명의 교차점 특별편 — PSP 한글패치

PSP 일본판 **《街 ～運命の交差点～ 特別篇》**을 한국어로 즐길 수 있는 비공식 패치입니다.
본문과 TIP, 메뉴를 번역하고 일부 그래픽과 동영상의 일본어 문구를 한글로 바꿨습니다.

**배포 버전: R42**

**[한글패치 다운로드](https://github.com/ayaneros-eng/machi-psp-korean-patch/releases/latest)**

Releases의 **`Machi_PSP_Korean_R42.zip`**을 받으세요. 자동으로 붙는 `Source code` 파일에는 패치 데이터가 없습니다.
일본판 원본 ISO가 필요하며, 이전 한글패치는 필요하지 않습니다. 게임 이미지 자체는 배포하지 않습니다.

## 한글 화면

| 타이틀 | 본문 |
| --- | --- |
| ![한글 타이틀 화면](screen-title.png) | ![케이마의 도입부](screen-story.png) |
| 주인공 선택 | 불러오기 |
| ![주인공 선택 화면](screen-characters.png) | ![한글 장면 제목과 불러오기 메뉴](screen-load.png) |

## 적용 방법

Windows에서는 다음 순서로 적용할 수 있습니다.

1. [Python 3.11.9](https://www.python.org/downloads/release/python-3119/)의 **Windows installer (64-bit)**를 설치합니다. 설치 항목의 Python Launcher도 포함해 주세요.
2. `Machi_PSP_Korean_R42.zip`을 새 폴더에 풉니다. 여유 공간은 **5GB 이상**을 권장합니다.
3. 일본판 원본 ISO를 **`apply_patch.cmd` 위로 끌어다 놓습니다.**
4. 완료 메시지가 나오면 같은 폴더에 생성된 **`Machi_R42_Korean.cso`**를 실행합니다.

원본은 그대로 유지됩니다. 같은 이름의 결과 파일이 이미 있으면 덮어쓰지 않고 중단합니다.

터미널에서 직접 적용할 수도 있습니다. 압축을 푼 폴더에서 실행하세요.

```powershell
py -3.11 -X utf8 apply_patch.py --source "original.iso" --output "Machi_R42_Korean.cso"
```

`original.iso` 부분은 가지고 있는 원본의 파일명 또는 경로로 바꾸면 됩니다. 별도의 Python 패키지 설치는 필요하지 않습니다.

## 지원하는 원본

| 항목 | 값 |
| --- | --- |
| 기종 | PSP |
| 대상 | 일본판 《街 ～運命の交差点～ 特別篇》 |
| 제품 번호 | ULJM-05111 |
| 입력 형식 | 압축하지 않은 ISO |
| 원본 크기 | 1,542,422,528바이트 |

원본 ISO의 SHA-256:

```text
48C5DF78FA7EBDDFB80DBC249BE211DB759678539976B8B45A9D9972A565488F
```

파일명이 달라도 크기와 해시가 일치하면 됩니다. CSO나 다른 판본, 이미 수정된 ISO는 직접 적용 대상이 아닙니다.

## 현재 버전에서 알아둘 점

- 일부 화면은 글꼴의 크기·두께·간격이 완전히 통일되지 않았습니다. 추가 정리는 후속 작업으로 남겨 두었습니다.
- 일본어 글자의 위치나 모양이 풀이에 필요한 암호는 원문을 유지하고 한글 설명을 보완했습니다.
- 크레딧과 마지막 회상 몽타주의 일본어는 원문을 유지했습니다. 배경 속 간판 등 일부 일본어도 남아 있습니다.
- 화면과 진행 검수는 PPSSPP에서 했습니다. PSP 본체에서의 동작은 별도로 검증하지 않았습니다.

## 적용 오류가 날 때

- **`Original ISO size/SHA256 does not match`**: 원본이 위 기준과 다릅니다. 파일명을 바꾸는 것으로 해결되지 않습니다.
- **`Output already exists`**: 다른 결과 파일명을 지정하거나 기존 결과를 다른 폴더로 옮긴 뒤 다시 적용하세요.
- **`Insufficient free space`**: 저장 공간을 확보한 뒤 다시 실행하세요.
- **`CISO index mismatch` / `Output SHA256 mismatch`**: 검증된 환경은 **Python 3.11.9 / zlib 1.3.1**입니다. 압축 라이브러리가 다른 환경에서는 결과가 달라질 수 있습니다. 안내한 Windows 환경으로 다시 적용하세요.

성공하면 `ORIGINAL_JP_TO_EXACT_R42_REBUILD_PASS`가 표시됩니다. 오류로 끝난 결과 파일은 사용하지 마세요.

완성된 CSO는 1,712,404,852바이트이며 SHA-256은 다음과 같습니다.

```text
8FEFB36146E179B1A02343448C7A110DCD069413E079AAD9A8BD4CE661A7A650
```

오탈자나 화면 잘림을 발견하면 [Issues](https://github.com/ayaneros-eng/machi-psp-korean-patch/issues)에 주인공·날짜·장면과 화면샷을 남겨 주세요. 결말에 관한 내용은 제목에 스포일러 표시를 부탁드립니다.

원작의 저작권은 각 권리자에게 있습니다.
