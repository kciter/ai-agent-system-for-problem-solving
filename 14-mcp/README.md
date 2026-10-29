# 14장 도구 연결의 표준 MCP

7장의 웹 검색과 페이지 읽기 도구를 MCP 서버로 만들고, 클라이언트로 연결해 도구를 부르고, 13장의 등록부에 MCP 도구를 올려 에이전트가 쓰게 합니다.

## 파일

| 파일 | 내용 | 책의 위치 |
|---|---|---|
| `research_server.py` | MCP 서버(`search_web`, `read_webpage`) | 14장 '구현: MCP 서버 만들기' |
| `client_test.py` | 서버에 연결해 도구 목록을 받고 `search_web`을 한 번 호출 | 14장 '구현: 에이전트에서 MCP 서버 사용하기' |
| `mcp_tools.py` | `register_mcp_tools`(책 코드), `make_mcp_caller`(예제 보충) | 같은 절의 등록 어댑터 |
| `main.py` | MCP 도구로 13장 에이전트를 실행하는 조립 코드(예제 보충) | 책에 없음 |
| `agent.py` | 8장 `call_llm`(재시도, 로깅)과 13장 코어(`TOOLS`, `tool`, `hook`, `run_hooks`, `run_agent`, `load_plugins`) | 8장, 13장에서 가져옴 |
| `plugins/approval.py`, `plugins/audit.py` | 승인 게이트 훅, 감사 로그 훅 | 13장에서 가져옴 |

## 책과 다른 점

- `client_test.py`의 마지막 줄 `asyncio.run(main())`을 `if __name__ == "__main__":` 아래로 옮겼습니다. `main.py`에서 import할 때 바로 실행되지 않게 하기 위해서입니다.
- `make_mcp_caller`는 책이 구현을 일부러 생략한 함수입니다. 이 함수가 없으면 `register_mcp_tools`를 실행할 수 없어서, 책의 설명대로 최소 구현을 넣었습니다. 설명은 두 가지입니다. "도구 이름을 받아 `session.call_tool`을 대신 호출해주는 함수를 만들어 반환한다", 그리고 "비동기 호출을 동기로 감싸는 배관이 필요하다". 구현은 `register_mcp_tools`가 불릴 때(세션이 열린 이벤트 루프 안) 그 루프를 기억해 두고, 다른 스레드에서 도는 13장 코어 루프가 `asyncio.run_coroutine_threadsafe`로 `session.call_tool`을 부르게 합니다. 결과(`CallToolResult`)를 문자열로 바꾸는 일은 하지 않았습니다. 책이 이 함수의 일로 말하지 않은 부분이라서입니다. 그래서 코어 루프의 `str(data["result"])`가 `meta=None content=[TextContent(type='text', text='...')]` 같은 파이썬 표현을 대화에 넣습니다. 모델은 그 안의 텍스트를 읽을 수 있지만, 깔끔하게 하려면 `make_mcp_caller`에서 `result.content`의 텍스트만 이어 붙여 돌려주면 됩니다.
- `main.py`는 책에 없는 조립 코드입니다. 플러그인 불러오기, 서버 연결과 `initialize`, `list_tools`, `register_mcp_tools`, `run_agent`를 잇습니다. 동기 함수인 `run_agent`는 이벤트 루프를 막지 않도록 `asyncio.to_thread`로 다른 스레드에서 돌립니다. 서버 실행 설정은 `client_test.py`의 `server_params`를 그대로 가져다 씁니다.
- 책이 보여주지 않는 import 줄을 넣었습니다. `mcp_tools.py`의 `import asyncio`, `from agent import TOOLS`, 플러그인 파일의 `from agent import hook`입니다.
- `agent.py`는 13장의 코어를 옮겨 온 것입니다. 8장의 `call_with_retry`, `call_llm`, `write_log`와 8장 최종 클라이언트 `OpenAI(timeout=30.0, max_retries=0)`가 들어 있습니다. 3장처럼 `.env`를 읽는 `load_dotenv()` 두 줄을 더했습니다. 14장에서 쓰지 않는 13장 코드(스킬, 히스토리 요약 훅, 웹 도구 플러그인)는 넣지 않았습니다. 웹 도구는 MCP 서버가 대신합니다.
- 더한 줄에는 모두 `# [예제 보충]` 주석을 달았습니다.

## 실행

```bash
uv sync
uv run client_test.py                   # 서버를 띄워 도구 목록을 보고 search_web을 한 번 호출
echo "OPENAI_API_KEY=sk-..." > .env
uv run main.py                          # MCP 도구로 리서치 에이전트 실행
```

- 이 디렉터리에서 실행하세요. 서버 스크립트(`research_server.py`)와 `plugins`를 현재 디렉터리 기준으로 찾습니다.
- 책의 `client_test.py`는 서버를 `command="python"`으로 띄웁니다. `uv run`으로 실행하면 가상 환경의 `python`이 쓰입니다. uv 없이 실행할 때 맥처럼 `python` 명령이 없고 `python3`만 있는 환경에서는 `FileNotFoundError: ... 'python'`이 나므로, 가상 환경을 활성화한 상태에서 실행하세요.
- 서버는 실제 웹을 검색합니다. ddgs가 남기는 INFO 로그가 표준 오류로 함께 출력될 수 있습니다.
