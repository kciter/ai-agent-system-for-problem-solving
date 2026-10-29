# 16장 코딩 에이전트 만들기

작업 디렉터리 안의 코드를 읽고, 고치고, 실행해 확인하는 코딩 에이전트입니다. 13장의 플러그인 구조 위에 파일 도구 다섯 개와 명령 실행 도구, 승인 게이트, 감사 로그, 히스토리 압축을 올립니다.

## 파일

| 파일 | 내용 | 책의 위치 |
|---|---|---|
| `agent.py` | 코어: `call_with_retry`, `call_llm`(8장), `TOOLS`/`tool`, `HOOKS`/`hook`/`run_hooks`, `load_plugins`(13장), `CODING_SYSTEM_PROMPT`, `run_turn`, `coding_agent` | '구현: 에이전트 조립', 8장, 13장 |
| `main.py` | `coding_agent()` 실행 | '구현: 에이전트 조립' 블록의 마지막 줄 |
| `plugins/code_tools.py` | `WORKSPACE`, `safe_path`, `read_file`, `search_code`, `edit_file`, `write_file`, `list_files`, `run_command` | '구현: 안전한 파일 도구', '구현: 명령 실행과 승인 게이트' |
| `plugins/approval.py` | `DANGEROUS_PATTERNS`, 승인 훅 `approve_commands` | '구현: 명령 실행과 승인 게이트' |
| `plugins/audit.py` | 감사 로그 훅 `audit_tool_calls` | 13장 '확장 지점 2: 훅' |
| `plugins/history.py` | `summarize_history`(5장), 히스토리 압축 훅 `compact_history`(13장) | 5장, 13장 |
| `workspace/` | 예시 프로젝트: `calculator.py`(0 나누기 처리 없음)와 `test_calculator.py`(테스트 5개) | '실행 결과'에서 말로만 설명한 파일 |
| `workspace/pytest.ini` | 작업 공간을 독립된 pytest 프로젝트로 다루게 하는 빈 설정 | |

## 책과 다른 점

- 파일 배치: 본문(305쪽)은 여섯 도구와 승인 훅, 감사 로그 훅을 "13장의 방식대로 plugins 디렉터리 아래 파일들에 나누어 두었다고 가정"할 뿐 파일 이름과 조립 코드의 위치는 밝히지 않습니다. 13장의 프로젝트 구조(`agent.py`는 코어, `main.py`는 실행, `plugins/`는 확장)를 그대로 따랐고, 플러그인 파일 이름은 예제에서 정했습니다.
- 책의 조립 블록 끝에 있는 `coding_agent()` 호출은 `agent.py`가 아니라 `main.py`의 `if __name__ == "__main__":` 아래에 두었습니다. `agent.py`에 두고 `python agent.py`로 실행하면 플러그인이 `agent`를 다시 import하면서 13장(266~267쪽)에서 설명한 이중 import 문제가 생기고, 승인 게이트가 등록되기 전에 세션이 한 번 더 돕니다.
- 플러그인 파일 첫 줄의 `from agent import tool`, `from agent import hook`, `from agent import hook, client`와 `main.py`의 `from agent import coding_agent`, 3장처럼 `.env`를 읽는 `load_dotenv()`는 책이 말로만 전제한 연결 코드입니다(`# [예제 보충]` 표시).
- 앞 장에서 가져온 코드: 8장의 재시도와 `call_llm`(클라이언트는 8장의 최종 설정 `OpenAI(timeout=30.0, max_retries=0)`이고 '사용 예' 호출은 뺐습니다), 13장의 레지스트리·훅·플러그인 로더·감사 훅·`compact_history`, 5장의 `summarize_history`입니다.
- `workspace/`의 `calculator.py`와 `test_calculator.py`는 책의 실행 결과를 따라 해볼 수 있게 예제에서 만들었습니다. 책의 세션처럼 처음에는 `test_divide_by_zero`가 실패합니다.

## 실행

이 디렉터리에서 실행하세요. 플러그인(`plugins/`)과 작업 디렉터리(`workspace/`)를 현재 디렉터리 기준으로 찾습니다.

```bash
uv sync
echo "OPENAI_API_KEY=sk-..." > .env
uv run main.py
```

```
> divide 함수가 0으로 나눌 때 처리가 없어. 고치고 테스트도 돌려줘.
```

에이전트가 `workspace/`의 파일을 실제로 고칩니다. 다시 해보려면 `git checkout -- workspace`로 원래 내용으로 되돌리세요. 명령은 실행 전에 모두 승인을 묻지만, 승인한 명령은 이 컴퓨터에서 그대로 실행됩니다.

`uv run`으로 실행하면 에이전트가 실행하는 `python -m pytest`도 이 장의 가상 환경에 설치된 파이썬과 pytest를 씁니다. uv 없이 실행할 때 셸에 `python` 명령이 없으면(맥) 에이전트의 `python -m pytest`가 실패하므로, 가상 환경을 켜고 실행하세요.

`workspace/pytest.ini`는 이 작업 공간을 독립된 pytest 프로젝트로 다루게 하는 빈 설정입니다.
