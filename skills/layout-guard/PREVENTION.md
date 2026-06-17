# PREVENTION — 겹침을 생성 시점에 구조적으로 막는 규칙

> 근본 원인: **Claude는 텍스트의 실제 bounding box를 계산할 수 없다.** 폰트
> 메트릭·줄바꿈·언어(한글이 넓음)·굵기(NanumSquare Bold)는 렌더 엔진만 안다.
> 그래서 절대좌표 + 고정 크기로 "예쁜 위치"를 노리면 추정이 빗나가는 순간 겹침이
> 발생한다. 아래 규칙은 *추정이 빗나가도* 레이아웃이 스스로 밀려나 깨지지 않게 한다.
> 이걸 지키면 검증 게이트에서 잡힐 이슈의 대부분이 애초에 생기지 않는다.

---

## 공통 원칙 (모든 매체)

1. **content가 box를 정하게 하라 (content-driven), box가 content를 자르게 하지 마라.**
   고정 높이 박스에 가변 텍스트를 넣지 말 것. 박스가 내용에 맞춰 늘어나거나,
   넘치면 줄어드는 구조를 쓴다.
2. **절대좌표는 최후 수단.** flow/grid/flex로 배치하면 추정 오차가 자동 흡수된다.
   절대좌표(`position:absolute`, pptx 고정 textbox)는 겹침 오차를 그대로 노출한다.
3. **여백을 자산으로.** 캔버스 가장자리 80px(HTML) / 0.4in(PPTX) safe-zone을
   비워 둔다. 빡빡하게 채우면 추정 1줄 오차가 곧 넘침이 된다.
4. **한글·Bold는 1.3~1.6배 넓게 잡아라.** Latin 기준으로 칸을 잡으면 한글에서 넘친다.

---

## HTML (덱 + 리포트)

### 레이아웃
- 카드/패널은 **flexbox 또는 grid**. 절대좌표 금지 (배지·각주 등 의도적 overlay 제외).
- 컬럼/카드 컨테이너에 `min-height: 0; overflow: hidden` (grid/flex 자식이
  intrinsic content로 부풀어 캔버스를 뚫는 대표 버그 차단 — slide-audit 카탈로그).
- 이미지: `max-height: <칸의 %>; object-fit: contain; flex: 0 1 auto; min-height: 0`.
  raw 이미지의 intrinsic height가 칸을 밀어내는 것을 막는다.
- 고정 덱(1920×1080): `240(top) + content-h + gap + 60(footer) + 80(safe) ≤ 1080`.
  content-h는 여유 있게(예: 620). 빡빡하게 1040까지 쓰지 말 것.

### 텍스트
- 제목과 pagenum/우상단 요소는 **같은 행에서 grid 2칸**으로 분리하고 title에
  `min-width: 0; overflow: hidden; text-overflow: ellipsis`. 길어져도 겹치지 않는다.
- 긴 텍스트 블록은 `overflow-wrap: anywhere` 또는 컨테이너 `overflow: hidden`로
  넘침을 가두고, 폰트는 `clamp()`로 가변.
- 본문 폰트: 절대 px 고정보다 `clamp(min, vw기반, max)`. 줄 수가 늘어도 칸을 안 넘게.

### 자가 점검(생성 직후, 게이트 전에 한 번)
- "이 칸에 들어갈 텍스트가 내가 가정한 줄 수보다 많아지면 어디로 가는가?"를
  요소마다 자문. "옆으로/아래로 흘러 겹친다"가 답이면 그 요소는 flow/clip로 고친다.

---

## PPTX

> python-pptx는 autofit을 신뢰 불가하게 적용하고, 박스 밖으로 흘러도 경고가 없다.
> OMML 수식 빈칸 버그까지 겹친다(feedback_pptx_recurring). 그래서 PPTX는 생성 시점
> 규칙이 특히 중요하다.

- **textbox에 autofit 명시**: `tf.word_wrap = True` +
  `tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE` (넘치면 폰트 축소). 단,
  본문 가독 폰트(예: ≥14pt) 하한을 두고, 그보다 작아질 분량이면 슬라이드를 나눈다.
- **박스 크기는 분량으로 역산.** 한글 1줄 ≈ `box_width_pt / font_pt`자.
  제목/본문 박스를 겹치게 배치하지 말 것 — 두 박스 rect가 교차하면 무조건 겹침.
- **safe-zone**: 슬라이드 4변에서 0.4in 안쪽에만 콘텐츠. 16:9 = 13.33×7.5in.
- **그림+캡션**은 그룹이 아니라 세로 스택(그림 박스 아래 별도 캡션 박스, 간격 0.1in).
- 슬라이드당 정보량이 많으면 **나눈다**. 한 장에 욱여넣는 게 겹침의 1번 원인.
- `\n`은 run 안에서 줄바꿈이 안 된다 — 단락(paragraph)을 분리해야 한다.

---

## 합성 figure (matplotlib / PIL)

- matplotlib: `constrained_layout=True` 또는 `fig.tight_layout()`,
  저장은 `bbox_inches='tight'`. 범례는 가능하면 `bbox_to_anchor`로 axes 밖.
- 범례 위치는 `loc='best'`를 신뢰(feedback_legend_position_rule) — 수직 강제 금지.
- 라벨은 `transAxes` 상대좌표로 (feedback_figure_label_protocol). offset 누적 주의.
- PIL compose: 레이아웃 엔진이 없으므로 **그리기 전에 `draw.textbbox()`로 각
  텍스트의 실제 px를 측정**하고 좌표를 잡는다. 좌표를 눈대중으로 박지 말 것
  (feedback_scheme_workflow: PIL 좌표 실측). 측정한 bbox는 `measure_figure.check_pil`로 교차검사.
- 코드는 반드시 `.py`로 저장(feedback_code_preservation: compose.py 유실 교훈).
