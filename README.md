[English](README.en.md) · **한국어**

# Claude Code Skills & Agents

A collection of custom [Claude Code](https://claude.com/claude-code) skills and
subagents built and used in a real research workflow — scientific writing,
presentation QA, figure/document tooling, and media pipelines.

These are modular: each skill is self-contained in its own folder with a
`SKILL.md` (and optional helper script). Take what is useful, ignore the rest.

## 설치

```
# Claude Code 사용자 디렉터리에 복사
cp -r skills/*  ~/.claude/skills/
cp    agents/*  ~/.claude/agents/
```

Windows PowerShell:

```
Copy-Item skills\* "$HOME\.claude\skills\" -Recurse
Copy-Item agents\* "$HOME\.claude\agents\"
```

복사 후 Claude Code를 재시작하면 스킬/에이전트가 인식된다.

## 스킬과 에이전트의 관계

이 저장소에는 **스킬(skill)**과 **에이전트(agent)**가 함께 있다. 둘은
역할이 다르다:

- **스킬** = 재사용 가능한 지식·규칙. "이 작업은 이렇게 한다"를 정의한다.
- **에이전트** = 그 스킬을 자율적으로 실행하는 서브에이전트.

그래서 `paper-sections`(스킬)과 `paper-section-drafter`(에이전트),
`paper-style`(스킬)과 `paper-style-enforcer`(에이전트)처럼 짝을 이루는
경우가 있다. 이는 중복이 아니라 "규칙"과 "그 규칙을 돌리는 실행기"의
의도된 분리다. 스킬만 단독으로 써도 되고, 에이전트로 자동화해도 된다.

## 수록 목록

### 과학 글쓰기 · 인용 — Scientific Writing & Citation

- **paper-sections** `skill` — IMRAD 섹션(Intro/Methods/Results/Discussion/
  Outlook) 작성 플레이북 + numeric-superscript 인용 포맷 규칙.
- **paper-style** `skill` — 저자 STYLE_PROFILE 로드 또는 경량 AI-ism
  정리(humanize).
- **paper-section-drafter** `agent` — IMRAD 섹션 초안을 STYLE_PROFILE
  준수하에 저자 voice로 작성, 가정·데이터 공백을 함께 반환.
- **paper-scientific-critic** `agent` — 단락/섹션의 방법론적 엄밀성·
  주장-근거 정합·논리 결함·과대주장 비평.
- **paper-style-enforcer** `agent` — STYLE_PROFILE 기계적 준수 검사(금지어·
  문장 길이·수사 의문문·hedge 스택·figure 인용 패턴).
- **paper-ref-hunter** `agent` — 레퍼런스 HUNT(특정 인용 → Crossref DOI
  확정) / DISCOVERY(주제 → OpenAlex 후보 랭킹) 2모드. DOI 날조 금지.
- **reference-crosscheck** `skill` — `.hwp`(바이너리)/`.hwpx`(OWPML)/`.docx`
  인용·참고문헌 교차검증: phantom·orphan·번호 불일치·중복·multiloc 검출
  + Tier2 Crossref 실재 검증(paper-ref-hunter 호출). 원본 무수정, 주석
  사본 + md/JSON 리포트. 757줄 엔진 `refcheck.py`. (python-docx, lxml)

### 데이터 분석 · figure — Data Analysis & Figures

- **analysis-protocol** `skill` — 스펙트럼 peak-fitting/deconvolution 검증
  게이트. lmfit 결과를 quant/visual(hard)·sanity(soft)로 검사해 나쁜
  fit이 figure·주장으로 새는 걸 차단. NH3-TPD/Py-DRIFTS/TPO/XPS/XRD 범용.
  (numpy, lmfit)
- **matplotlib-scientific** `skill` — 출판용 matplotlib figure 규칙
  (폰트 스택, 300 DPI SVG, 레이아웃 제어). (matplotlib)

### 문서 · 리포트 — Documents & Reports

- **docx-scientific-formatting** `skill` — .docx 화학/물리 표기(아래첨자·
  위첨자·이탤릭 오비탈·화학식) 일괄 정리. (python-docx, lxml)
- **html-minimal** `skill` — 미니멀 HTML 문서 디자인 시스템(절제된
  타이포·여백 구조).

### 프레젠테이션 — Presentation

- **layout-guard** `skill` — HTML·PPTX·matplotlib/PIL figure 전반의 글자/요소
  겹침·넘침을 막는 범용 가드. 생성 시점 예방 규칙 + 전달 직전 결정론 measure
  게이트(겹침·overflow 검출) + 안전 자동보정. PPTX는 XML triage → LibreOffice/
  PowerPoint 렌더 권위 검증. slide-audit(HTML 덱)을 전 매체로 일반화.
  (Node.js, Playwright, python-pptx)
- **slide-audit** `skill` — HTML 슬라이드 덱을 Playwright로 PNG 렌더 +
  bounding-rect 진단 + 서브에이전트 시각 검수. 글자 겹침·잘림·오버플로
  검출. (Node.js, Playwright)

### 미디어 — Media

- **youtube** `skill` — YouTube transcript + 메타데이터 + 스마트 프레임
  캡처(heatmap peak / chapter / 균일 간격)를 타임스탬프 Markdown으로.
  (yt-dlp, ffmpeg)
- **youtube2mp4** `skill` — YouTube 영상 MP4 다운로드(해상도 캡·오디오
  only·구간 트림). (yt-dlp, ffmpeg)
- **transcript2html** `skill` — YouTube transcript.md → 정리된 Markdown +
  다크모드 HTML(프레임·풀쿼트·번역) 변환. 다크 템플릿 포함.

### 3D · 유틸 — 3D / Utility

- **blender-atom-render** `skill` — 구조 파일(traj/xyz)에서 개별 원자 구
  렌더 + 시스템별 레전드 생성. (Blender, ASE, Pillow)
- **smart-compact** `skill` — 세션 상태를 `.claude/session-state.md`로
  저장해 `/clear` 이후 복구.

## 의존성

스킬별로 다름 — 위 괄호 표기 참고. 공통적으로 Python 3.9+ 환경을 가정하며,
`slide-audit`·`layout-guard`가 Node.js + Playwright를 쓴다. `layout-guard`의
PPTX 검사는 python-pptx(렌더 권위 검증 시 LibreOffice 또는 PowerPoint 추가).

## 참고

- `paper-*` 스킬·에이전트는 사용자가 직접 작성한
  `~/.claude/paper-team/STYLE_PROFILE.md`(자신의 글쓰기 규칙)를 참조한다.
  이 저장소에는 그 프로필이 **포함되지 않으며**, 각자 자신의 것을 만들어
  넣어야 한다.
- 일부 스킬은 다른 스킬/슬래시 커맨드를 참조한다(예: `transcript2html` ←
  `youtube`). 단독으로도 동작하지만 함께 쓰면 흐름이 매끄럽다.

## License

MIT — see [LICENSE](LICENSE).
