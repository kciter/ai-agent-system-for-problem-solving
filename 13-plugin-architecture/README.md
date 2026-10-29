# 13장 플러그인 아키텍처

도구 레지스트리, 훅, 스킬이라는 세 확장 지점을 갖춘 에이전트 코어와, 책의 프로젝트 구조대로 나눈 플러그인 파일들입니다. 7장의 리서치 에이전트를 플러그인과 스킬로 다시 조립합니다.

## 파일

| 파일 | 내용 | 책의 위치 |
|---|---|---|
| `agent.py` | 코어: 8장 신뢰성 계층(`call_llm`), `TOOLS`/`tool`, `HOOKS`/`hook`/`run_hooks`, `load_skill`/`apply_skill`, `run_agent`, `load_plugins` | 13장 '확장 지점 1: 도구 레지스트리'부터 '구현: 코어 루프의 완성'까지 |
| `main.py` | 플러그인을 불러오고 스킬을 붙여 에이전트를 실행하는 파일 | 13장 '구현: 코어 루프의 완성' 마지막 코드 |
| `plugins/web_tools.py` | `search_web`, `read_webpage` 등록 | 13장 '확장 지점 1', 함수 본문은 7장 |
| `plugins/approval.py` | 승인 게이트 훅(`before_tool`) | 13장 '확장 지점 2: 훅' |
| `plugins/audit.py` | 감사 로그 훅(`after_tool`) | 13장 '확장 지점 2: 훅' |
| `plugins/history.py` | 히스토리 요약 훅 `compact_history`(`before_llm`)와 5장의 `summarize_history` | 13장 '확장 지점 2: 훅', 5장 '세계관 일관성 유지' |
| `skills/competitor-research.md` | 경쟁사 조사 스킬 | 13장 '확장 지점 3: 스킬' |

## 책과 다른 점

- 책은 플러그인 파일과 `main.py`의 import 줄을 보여주지 않고 "플러그인이 agent 모듈을 임포트한다"(266~267쪽)고 설명만 합니다. `from agent import tool`, `from agent import hook`, `from agent import load_plugins, run_agent, apply_skill` 같은 줄을 `[예제 보충]`으로 넣었습니다.
- `agent.py` 앞부분의 `client`, `call_with_retry`, `call_llm`, `write_log`는 8장 코드를 그대로 가져왔습니다. 책은 신뢰성 계층을 포함한 LLM 호출이 코어에 남는다고만 합니다(257쪽).
- `plugins/web_tools.py`: 책은 `search_web`의 등록 코드만 보여주고 본문은 "7장과 동일"이라고 합니다. 본문과 `read_webpage`는 7장에서 가져왔고, `read_webpage`의 `@tool(...)`은 `search_web`과 같은 방식으로 7장 `tools` 배열의 설명과 파라미터를 옮겼습니다(`[예제 보충]`). 책의 `search_web` 스키마에는 7장과 달리 `max_results`가 없는데, 책 그대로 두었습니다.
- `plugins/history.py`: 책의 프로젝트 구조에는 없지만, 본문이 히스토리 요약을 `before_llm` 훅으로 옮기므로 플러그인 파일로 두었습니다. 그래서 `python main.py`를 실행하면 이 훅도 함께 등록됩니다(메시지가 20개를 넘을 때만 동작). `summarize_history`는 5장 코드 그대로입니다.
- `skills/competitor-research.md`: 책 코드 블록의 첫 줄 `# skills/competitor-research.md`는 파일 이름 표시라서 파일 내용에서 뺐습니다.
- `main.py`는 책 그대로 `if __name__ == "__main__":` 가드가 없습니다. import해서 쓰는 파일이 아니기 때문입니다. `system_prompt` 끝의 `...`도 책 그대로이니, 실제로 쓸 때는 7장의 `RESEARCH_SYSTEM_PROMPT`처럼 채우세요.
- `plugins/__init__.py`는 책 설명(266쪽)대로 두지 않았습니다.

## 실행

`agent.py`가 있는 이 디렉터리에서 실행하세요.

```bash
uv sync
echo "OPENAI_API_KEY=sk-..." > .env
uv run main.py
```

다른 위치에서 `uv run 경로/main.py`로 실행하면 오류 없이 플러그인과 스킬이 하나도 없는 채로 돕니다. 호출 로그는 실행한 디렉터리의 `llm_calls.jsonl`에 쌓입니다.
