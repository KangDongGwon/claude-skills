---
name: layout-guard
description: Universal overlap/overflow guard for ANY generated HTML, PPTX, or composed figure — the cross-cutting "글씨 겹침" fix. Two layers - (1) PREVENTION rules injected at generation time so overlap can't form by construction, (2) a deterministic measure→safe-autofix→flag verification GATE run before any visual artifact is delivered. Generalizes slide-audit (HTML decks) to general HTML reports, PPTX, and matplotlib/PIL figures. Triggers - 겹침, 글자 겹침, 글씨 겹침, 텍스트 겹침, 레이아웃 깨짐, 넘침, overflow, overlap, 박스 밖으로, 잘림, clipping, 산출물 검수, layout guard, 겹침 보정, figure 라벨 겹침, ppt 겹침, html 겹침. ALSO invoke as a silent pre-delivery gate whenever this session produces an .html / .pptx / composed figure.
---

# layout-guard

생성물(HTML·PPTX·figure)의 **겹침/넘침을 막는 범용 가드**. 매번 사용자가 "겹친다
고쳐라"를 반복하던 근본 원인 — *Claude가 텍스트의 실제 bounding box를 계산할 수 없어
추정으로 배치한다* — 를 두 층으로 차단한다.

```
PREVENTION (생성 시점)   →   GATE: measure → safe-autofix → flag (전달 직전)
구조적으로 안 생기게        남은 것만 결정론적으로 측정·보정·플래그
```

`slide-audit`(HTML 덱 한정)의 *"rect는 거짓말 안 한다"* 교훈을 일반 HTML·PPTX·figure로
확장한 것. HTML 덱은 `slide-audit`에 위임 가능(아래 라우팅 참조).

## 언제 작동하나 (게이트 규약)

이 스킬은 두 방식으로 호출된다:

1. **명시 호출** — 사용자가 겹침/레이아웃 점검을 요청할 때.
2. **암묵 게이트 (핵심)** — 이 세션에서 `.html` / `.pptx` / 합성 figure를 **만들어
   사용자에게 넘기기 직전**, 모든 HTML/PPTX/figure 생성 스킬의 definition-of-done으로
   1회 실행한다. 통과(clean)면 조용히 넘어가고, 이슈가 있으면 안전 항목은 자동보정하고
   나머지는 플래그한다.

> 텍스트만 살짝 고친 산출물이거나 사용자가 직접 편집한 파일이면 게이트를 건너뛸 수
> 있다. 새로 생성/대량 수정한 시각 산출물에만 건다 (over-engineering 경계).

## 작동 순서

### 0. PREVENTION 적용 (생성 시점)
산출물을 *만들 때* `PREVENTION.md`의 매체별 규칙을 따른다. 이게 1차 방어선이고,
대부분의 겹침을 애초에 없앤다. 게이트는 백스톱이지 대체재가 아니다.

### 1. 매체 판별 → 엔진 라우팅

| 산출물 | 엔진 | 비고 |
|---|---|---|
| HTML **덱** (`.slide`+`.is-active`) | `slide-audit` 스킬 (measure.mjs + 시각 서브에이전트) | 이미 존재 → 위임. 더 풍부한 시각 검수 |
| HTML **덱 (범용/비표준 class)** | `measure_html.mjs --mode deck --slide-selector ... --active-class ...` | slide-audit 규약 밖일 때 |
| 일반 HTML 리포트 (스크롤 문서) | `measure_html.mjs --mode page` | 세로 성장은 정상, 가로 overflow·parent overflow·텍스트 겹침만 |
| PPTX | `measure_pptx.py` | XML 결정론, **COM 불필요**. 기본=기하학적 사실(edge-straddle·텍스트 shape 겹침 후보). `--overflow`=텍스트 넘침 휴리스틱(opt-in, dense/theme 덱서 과탐) |
| 합성 figure (matplotlib) | `measure_figure.check_mpl(fig)` | **savefig 전** 코드에 삽입. 렌더러 실측 bbox |
| 합성 figure (PIL) | `measure_figure.check_pil(boxes)` | draw 시 `textbbox`로 측정한 박스 전달 |

### 2. 측정 실행

HTML (설치 최초 1회):
```bash
cd ~/.claude/skills/layout-guard && [ -d node_modules/playwright ] || npm install
npx playwright install chromium
```
**중요**: Playwright 실행 Bash는 `dangerouslyDisableSandbox: true` (Chromium이
killEPERM로 죽음 — slide-audit과 동일 환경 이슈).

```bash
# 일반 HTML 리포트
node ~/.claude/skills/layout-guard/measure_html.mjs <html> --mode page
# 범용 덱
node ~/.claude/skills/layout-guard/measure_html.mjs <html> --mode deck --slide-selector .slide --active-class is-active
# PPTX
python ~/.claude/skills/layout-guard/measure_pptx.py <pptx> --json /tmp/lg.json
```
figure는 플로팅 스크립트 안에서:
```python
import os, sys; sys.path.insert(0, os.path.expanduser("~/.claude/skills/layout-guard"))
from measure_figure import check_mpl, report
hits = check_mpl(fig)          # fig.savefig() 직전
report(hits)                   # 이슈 있으면 보정 후 재측정
```

### 3. 안전 자동보정 vs 플래그
`AUTOFIX.md` 분류를 따른다.
- **안전(결정론적·내용불변·새 이슈 없음)** → 바로 보정하고 **재측정**.
  보정이 새 이슈를 만들면 롤백 → 플래그로 강등.
- **그 외**(텍스트끼리 겹침의 의도성 모호, 내용삭제 필요, 사용자 편집 흔적,
  휴리스틱 신호) → **플래그만**. 자동으로 내용을 지우지 않는다(말소 금지).

### 4. 보고
자동보정 항목은 `feedback_change_report_with_context` 4축(위치·원인·조치·근거)으로,
플래그 항목은 위치·증상·추정원인으로 보고. clean이면 한 줄("layout-guard: N scene clean").

## 한계 (정직 — 실측 검증 결과 반영)

실제 산출물 다수로 테스트해 false-positive를 제거한 상태(아래는 남은 본질적 한계).

**HTML (신뢰도 높음)** — 실제 리포트 4종 clean, synthetic 겹침 검출 통과.
- text-overlap은 **block 요소만** 비교한다. inline(em/strong/a/span)은 줄바꿈 시 rect가
  형제와 겹치는 정상 흐름이라 제외 — 안 그러면 산문에서 대량 오탐.
- 의도적 block overlay(배지·워터마크)는 여전히 오탐 가능 → 텍스트 겹침은 **플래그 전용**, 자동보정 안 함.

**PPTX (XML 한계 인지)** — XML은 렌더 결과(폰트 상속·autofit 성장·줄바꿈·placeholder
bbox)를 알 수 없어 pass/fail 게이트가 아니라 **triage(후보 발굴)**다.
- 기본 출력 = 기하학적 사실: **edge-straddle**(가장자리에 걸친 도형. 완전히 밖=parking은
  무시) + **텍스트 shape 겹침 후보**(양쪽 텍스트·placeholder 제외·>25% 교차). 완성덱은
  거의 clean, dense 덱은 후보 몇 건 — **"확인할 후보"로 다루고 시각 확인**.
- `--overflow`(opt-in) = 텍스트 넘침 휴리스틱. char-width·폰트 추정이라 theme-styled/dense
  덱서 과탐 → Claude 생성덱(명시 폰트)서만 권장.
- 정밀 pass/fail이 필요하면 **`render_pptx.py`로 실제 렌더 → PNG → 시각 서브에이전트**가
  권위본. 백엔드: LibreOffice(headless·세션 무위험·우선) → 없으면 PowerPoint COM. **COM은
  PowerPoint가 이미 떠 있으면 거부**(단일 인스턴스라 Quit 시 사용자 세션이 닫힘 —
  feedback_hwp_com_unsafe). 렌더 후 slide-audit 시각-서브에이전트 프롬프트를 그대로 적용.
- 그룹/자동배치 shape는 좌표 미해결로 skip.

**figure** — `savefig` 전 코드 삽입이 정석(렌더러 실측 bbox라 정확). 이미 PNG면 시각 판독만.

## 파일
- `PREVENTION.md` — 생성 시점 매체별 규칙 (1차 방어선, 생성 스킬이 참조)
- `AUTOFIX.md` — 안전 자동보정 vs 플래그 분류 + 보고 양식
- `measure_html.mjs` — 범용 HTML rect 검사기 (deck/page 모드)
- `measure_pptx.py` — PPTX XML 결정론 triage (off-slide-straddle·겹침 후보·`--overflow`)
- `render_pptx.py` — PPTX 권위 렌더 (LibreOffice/PowerPoint COM → PNG → 시각 검수)
- `measure_figure.py` — matplotlib/PIL 텍스트 bbox 겹침
- `package.json` — Playwright 의존성
