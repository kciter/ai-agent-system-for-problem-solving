# 15장 에이전트 프레임워크

7장 리서치 에이전트를 랭체인 `create_agent`로, 12장 리서치 팀을 랭그래프 그래프로 다시 만들고, 체크포인트와 휴먼 인 더 루프를 붙여 봅니다.

## 파일

| 파일 | 내용 | 책의 위치 |
|---|---|---|
| `step1_create_agent.py` | `@tool` 도구 두 개, `create_agent`, 최종 응답과 대화 기록 출력 | '에이전트 루프를 몇 줄로' |
| `step2_research_graph.py` | `ResearchState`, 노드 네 개, `should_rewrite`, 그래프 구성, `invoke` | '리서치 팀을 그래프로' |
| `step3_stream.py` | `stream_mode="updates"`로 노드별 갱신 보기 | '리서치 팀을 그래프로'의 stream 예 |
| `step4_checkpoint.py` | `InMemorySaver`와 `thread_id`로 실행 | '실행을 맡기면 생기는 것들'의 체크포인트 |
| `step5_human_in_the_loop.py` | `approve_node`, 바꾼 `should_rewrite`, `interrupt`와 `Command(resume=...)` | 같은 절의 휴먼 인 더 루프 |
| `research_team.py` | 그래프 노드가 부르는 앞 장의 함수: `search_web`, `read_webpage`, `run_research`, `write_report`(7장), `call_with_retry`, `call_llm`, `evaluate_report`(8장), `plan_subtopics`, `run_workers`(12장) | 7장, 8장, 12장 |

## 책과 다른 점

- 책의 코드를 단계마다 따로 실행할 수 있게 다섯 파일로 나눴습니다. 3~5단계는 2단계 파일에서 `app`, `graph`, 상태와 노드 함수를 가져옵니다(`# [예제 보충]` 표시).
- 각 단계의 실행 줄(`agent.invoke`, `app.invoke`, `app.stream`, `print`)은 `if __name__ == "__main__":` 아래로 옮겼습니다. 다른 파일에서 import할 때 바로 실행되지 않게 하기 위해서입니다.
- 1단계 도구 본문은 책에서 "함수 본문은 7장과 동일"이라며 `...`로 줄였으므로 7장 본문을 그대로 넣었습니다. 7장의 `RESEARCH_SYSTEM_PROMPT`는 `research_team.py`에서 가져오고, 3장처럼 `load_dotenv()`를 불러 `.env`의 키를 읽습니다.
- 5단계는 본문(290쪽)의 전제대로 `should_rewrite`를 바꾼 뒤 그래프 구성을 처음부터 다시 실행합니다. 2단계의 그래프 구성 코드를 그대로 다시 적었고, `config`는 4단계의 줄을 옮겼습니다.
- 4·5단계 실행부에는 결과를 확인하는 `print`를 더했습니다(5단계는 `interrupt`에 담긴 질문과 승인 뒤의 보고서).
- `research_team.py`는 7·8·12장 코드를 옮긴 것입니다. 12장 본문(244쪽)의 전제대로 `run_research`, `write_report`, `evaluate_report`의 LLM 호출은 8장처럼 `call_llm`으로 바꿨습니다. `run_research`의 `trace_id`는 8장 본문(192쪽) 설명대로 `uuid.uuid4()`로 만듭니다. 클라이언트는 8장의 최종 설정 `OpenAI(timeout=30.0, max_retries=0)`이고, 8장의 '사용 예' 호출과 7장의 마지막 `print(research_agent(...))`는 뺐습니다.
- 3~5단계의 주제는 책처럼 `"..."`입니다. 실제로 돌릴 때는 원하는 주제로 바꾸세요.

## 실행

```bash
uv sync
echo "OPENAI_API_KEY=sk-..." > .env
uv run step1_create_agent.py
uv run step2_research_graph.py
uv run step3_stream.py
uv run step4_checkpoint.py
uv run step5_human_in_the_loop.py
```

검색에 쓰는 ddgs는 키가 필요 없지만, 짧은 시간에 많이 검색하면 일시적으로 차단될 수 있습니다. 2~5단계는 워커 세 개가 동시에 검색합니다.
