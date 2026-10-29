# 7장 자동 리서치 에이전트

웹을 검색하고 페이지를 읽어 출처가 달린 조사 노트를 만든 뒤, 그 노트로 보고서를 쓰는 에이전트입니다.

## 파일

| 파일 | 내용 | 책의 위치 |
|---|---|---|
| `research_agent.py` | 기본 설정, `search_web`, `read_webpage`, 도구 정의, `run_research`, `write_report`, `research_agent` | 7장 '개발 환경 준비'부터 '구현: 보고서 작성'까지 |

책과 다른 점은 하나입니다. 마지막 실행 줄 `print(research_agent(...))`를 `if __name__ == "__main__":` 아래로 옮겼습니다. 다른 파일에서 이 파일을 import할 때 에이전트가 바로 실행되지 않게 하기 위해서입니다.

## 실행

```bash
uv sync
echo "OPENAI_API_KEY=sk-..." > .env
uv run research_agent.py
```

검색에 쓰는 ddgs는 무료라 키가 필요 없지만, 짧은 시간에 많이 검색하면 일시적으로 차단될 수 있습니다.
