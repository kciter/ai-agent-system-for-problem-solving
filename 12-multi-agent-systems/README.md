# 12장 멀티 에이전트 시스템

7장의 리서치 에이전트를 조사 워커로 써서 주제를 하위 질문으로 나눠 병렬로 조사하고, 보고서를 쓰고 검증하는 리서치 팀입니다. 제안자와 비판자가 반박을 주고받는 토론 패턴도 있습니다.

## 파일

| 파일 | 내용 | 책의 위치 |
|---|---|---|
| `research_team.py` | 7장 도구와 `run_research`, `write_report`, 8장 신뢰성 계층과 `evaluate_report`, 12장 `plan_subtopics`, `run_workers`, `research_team`, `orchestrator_tools`, `delegate_research` | 12장 '구현: 리서치 팀 만들기', '정적 위임과 동적 위임' |
| `debate.py` | 토론 패턴 `debate` | 12장 '남은 패턴: 토론' |

## 책과 다른 점

- `research_team.py` 앞부분에 7장과 8장의 코드를 가져왔습니다. 12장은 "8장 마지막에서 했던 대로 세 함수의 내부 호출이 모두 call_llm으로 교체된 버전"을 전제로 합니다. 8장은 이 교체를 `run_research`의 호출 하나만 코드로 보여주고 나머지는 글로 설명하므로, 글에 따라 `run_research`, `write_report`, `evaluate_report`의 LLM 호출을 `call_llm(trace_id=trace_id, ...)`로 바꾸고 `trace_id`는 각 함수가 시작할 때 `str(uuid.uuid4())`로 만들었습니다(`[예제 보충]`, 08-reliability 예제와 같은 방식).
- 7장, 8장, 12장 코드를 한 파일에 둔 것은 책이 한 파일을 전제로 설명하기 때문입니다(249쪽 "한 파일에서 같은 이름을 쓰면").
- `print(research_team(...))`는 책에서는 `research_team` 정의 바로 뒤에 있지만 파일 끝의 `if __name__ == "__main__":` 아래로 옮겼습니다. 다른 파일에서 import할 때 바로 실행되지 않게 하기 위해서입니다.
- 토론 패턴은 따로 실행할 수 있게 `debate.py`로 나눴습니다. `call_llm`은 `research_team.py`에서 가져옵니다(`[예제 보충]`). `print(debate(...))`도 `if __name__ == "__main__":` 아래에 있습니다.
- 동적 위임의 오케스트레이터 루프는 책이 "7장의 에이전트 루프와 똑같은 구조"라고 설명만 하고 코드는 보여주지 않으므로 만들지 않았습니다. `orchestrator_tools`와 `delegate_research`까지만 있습니다.

## 실행

```bash
uv sync
echo "OPENAI_API_KEY=sk-..." > .env
uv run research_team.py
uv run debate.py
```

세 워커가 동시에 검색하므로 ddgs의 일시 차단에 걸리기 쉽습니다(책 '워커 실행: 분배와 병렬화'의 주의 사항). 호출 로그는 `llm_calls.jsonl`에 쌓입니다.
