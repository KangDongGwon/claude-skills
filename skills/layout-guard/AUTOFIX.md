# AUTOFIX — 안전 자동보정 vs 플래그 전용

검증 게이트가 이슈를 찾으면, 아래 분류로 처리한다.
**"안전"의 정의**: 보정이 결정론적이고, 의미/내용을 바꾸지 않으며, 다른 요소를
새로 깨뜨릴 위험이 없는 경우. 그 외는 전부 **플래그만** 하고 사용자/별도 턴에서 결정.

---

## ✅ 안전 자동보정 (게이트가 바로 적용)

| 이슈 유형 | 조건 | 자동보정 |
|---|---|---|
| 텍스트 박스 넘침 (HTML) | 단일 컨테이너의 `scrollHeight > clientHeight` | 폰트 `clamp()` 하한까지 축소 → 그래도 넘치면 플래그 |
| footer/캔버스 overflow (덱) | content-h가 가용높이 초과 | `240 + content-h + gap + 60 + 80 ≤ 1080` 만족하도록 content-h 하향 |
| 컬럼/카드 캔버스 돌파 | grid/flex 자식 intrinsic 부풀음 | 컨테이너에 `min-height:0; overflow:hidden`, 이미지에 `max-height/object-fit` 주입 (slide-audit 카탈로그) |
| 가로 viewport overflow (리포트) | 요소가 캔버스 우측 1px+ 초과, 원인이 `white-space:nowrap`/고정 width | `overflow-wrap:anywhere` 또는 width 제약 완화 |
| PPTX textbox 넘침 | autofit 미설정 + 추정 넘침 | `word_wrap=True` + `auto_size=TEXT_TO_FIT_SHAPE` 주입 (폰트 하한 이상일 때만) |
| PPTX off-slide shape | 박스가 safe-zone 밖 | safe-zone 안으로 위치 clamp (다른 박스와 새 overlap 안 생길 때만) |
| matplotlib 라벨 겹침 | `tight_layout`/`constrained_layout` 미적용 | 해당 옵션 + `bbox_inches='tight'` 주입 후 재측정 |

자동보정 후 **반드시 재측정**. 보정이 새 이슈를 만들면 롤백하고 플래그로 강등.

---

## 🚩 플래그 전용 (자동보정 금지 — 사용자/별도 턴 결정)

- **텍스트끼리 겹침(text-overlap)** 으로 보고됐는데 두 요소가 의도적 overlay일 수
  있는 경우 (배지, 워터마크, 캡션 오버레이). 자동으로 떼면 디자인 의도를 깬다.
- **구조적 모호성**: 어느 요소를 줄여야 할지 콘텐츠 우선순위 판단이 필요한 경우.
- **내용 삭제가 유일한 해법**일 때. 텍스트/요소를 지우는 보정은 절대 자동 금지
  (deliverable_version_guard: 말소 금지). 분량 자체가 많으면 "슬라이드 분할" 제안.
- **PPTX shape-overlap** 중 한쪽이라도 사용자가 직접 배치한 흔적(편집됨)이 있으면
  건드리지 않는다 (feedback_user_edits_interpretation).
- **휴리스틱 신호** (PPTX text-overflow의 heuristic=true): 폰트 메트릭 추정이라
  확정 아님 → 플래그만, 자동보정은 명백한 케이스에 한정.

---

## 보정 보고 양식 (feedback_change_report_with_context 준수)

자동보정한 항목은 short label만 보고하지 말고 **위치 + 원문상태 + 변경후 + 근거**
4축으로 보고:

```
[자동보정] slide 7 / .card[2] 본문
  - 원인: scrollHeight 412 > clientHeight 360 (52px 넘침)
  - 조치: font-size clamp 하한(0.9rem) 적용 → 358px, 캔버스 내 수용
  - 근거: 내용·의미 불변, 가독 하한 유지
```

플래그 항목은 보정하지 말고 그대로 위치·증상·추정원인만 제시하고 결정을 넘긴다.
