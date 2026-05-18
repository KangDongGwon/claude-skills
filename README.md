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

## 수록 목록

### Skills

- **slide-audit** — HTML 슬라이드 덱을 Playwright로 PNG 렌더 + bounding-rect
  진단 + 서브에이전트 시각 검수. 글자 겹침·잘림·오버플로 검출. (Node.js, Playwright)
- **matplotlib-scientific** — 출판용 matplotlib figure 규칙(폰트 스택,
  300 DPI SVG, 레이아웃 제어). (matplotlib)
- **docx-scientific-formatting** — .docx 화학/물리 표기(아래첨자·위첨자·
  이탤릭 오비탈·화학식) 일괄 정리. (python-docx, lxml)
- **html-minimal** — 미니멀 HTML 문서 디자인 시스템(절제된 타이포·여백 구조).
- **transcript2html** — YouTube transcript.md → 정리된 Markdown + 다크모드
  HTML(프레임·풀쿼트·번역) 변환. 다크 템플릿 포함.
- **youtube** — YouTube transcript + 메타데이터 + 스마트 프레임 캡처
  (heatmap peak / chapter / 균일 간격)를 타임스탬프 Markdown으로. (yt-dlp, ffmpeg)
- **youtube2mp4** — YouTube 영상 MP4 다운로드(해상도 캡·오디오 only·구간 트림).
  (yt-dlp, ffmpeg)
- **blender-atom-render** — 구조 파일(traj/xyz)에서 개별 원자 구 렌더 +
  시스템별 레전드 생성. (Blender, ASE, Pillow)
- **reference-crosscheck** — `.hwp`(바이너리)/`.hwpx`(OWPML)/`.docx` 인용·
  참고문헌 교차검증. phantom(인용했으나 목록 없음)·orphan·번호 불일치·중복·
  multiloc 검출 + Tier2 Crossref 실재 검증. 원본 무수정, 주석 사본 + md/JSON
  리포트. 757줄 엔진 `refcheck.py`. (python-docx, lxml; Tier2는 paper-ref-hunter)
- **analysis-protocol** — 스펙트럼 peak-fitting/deconvolution 검증 게이트.
  lmfit 결과를 quant/visual(hard)·sanity(soft)로 검사해 나쁜 fit이 figure·
  주장으로 새는 걸 차단. NH3-TPD/Py-DRIFTS/TPO/XPS/XRD 범용. (numpy, lmfit)
- **paper-sections** — IMRAD 섹션(Intro/Methods/Results/Discussion/Outlook)
  작성 플레이북 + numeric-superscript 인용 포맷 규칙.
- **paper-style** — 저자 STYLE_PROFILE 로드 또는 경량 AI-ism 정리(humanize).
- **smart-compact** — 세션 상태를 `.claude/session-state.md`로 저장해
  `/clear` 이후 복구.

### Agents (subagents)

- **paper-section-drafter** — IMRAD 섹션 초안을 STYLE_PROFILE 준수하에 작성.
- **paper-scientific-critic** — 단락/섹션의 방법론적 엄밀성·주장-근거 정합·
  논리 결함·과대주장 비평.
- **paper-style-enforcer** — STYLE_PROFILE 기계적 준수 검사(금지어·문장 길이·
  수사 의문문·hedge 스택·figure 인용 패턴).
- **paper-ref-hunter** — 논문 레퍼런스 두 모드: HUNT(특정 인용 → Crossref
  DOI 확정), DISCOVERY(주제 → OpenAlex 후보 랭킹). DOI 날조 금지.
  `reference-crosscheck`의 Tier2 검증이 이걸 호출한다.

## 의존성

스킬별로 다름 — 위 괄호 표기 참고. 공통적으로 Python 3.9+ 환경을 가정하며,
`slide-audit`만 Node.js + Playwright가 필요하다.

## 참고

- `paper-*` 스킬·에이전트는 사용자가 직접 작성한
  `~/.claude/paper-team/STYLE_PROFILE.md`(자신의 글쓰기 규칙)를 참조한다.
  이 저장소에는 그 프로필이 **포함되지 않으며**, 각자 자신의 것을 만들어
  넣어야 한다.
- 일부 스킬은 다른 스킬/슬래시 커맨드를 참조한다(예: `transcript2html` ←
  `youtube`). 단독으로도 동작하지만 함께 쓰면 흐름이 매끄럽다.

## License

MIT — see [LICENSE](LICENSE).
