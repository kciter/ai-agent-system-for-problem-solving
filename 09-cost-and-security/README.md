# 9장 비용과 보안

8장 로그로 비용을 재고, 모델 선택과 캐싱으로 줄이며, 프롬프트 인젝션·개인정보·위험한 도구·임의 코드 실행에 대비합니다.

## 파일

| 파일 | 내용 | 책의 위치 |
|---|---|---|
| `cost.py` | `PRICE_PER_1M`, `calculate_cost`, `summarize_costs`, `cached_llm_call` | '비용의 구조', '캐싱: 호출 줄이기' |
| `research_agent.py` | 8장 리서치 에이전트에 `MODELS`와 보고서 작성 모델을 바꾼 `write_report`, `wrap_external_data`와 본문을 경계 표시로 감싸는 `read_webpage`를 더한 것 | '모델 선택', '프롬프트 인젝션' |
| `security.py` | `mask_pii`, `REQUIRES_APPROVAL`, `execute_tool`, `run_tool`(보충), `run_in_sandbox` | '개인정보와 데이터 보호', '권한 관리', '샌드박스: 실행 공간의 격리' |
| `reliability.py` | 8장 신뢰성 계층(`call_with_retry`, `call_llm`, `write_log` 등) | 8장 |

앞 장에서 가져온 코드:

- `reliability.py`는 `08-reliability/reliability.py`와 같은 파일입니다.
- `research_agent.py`는 `08-reliability/research_agent.py`(7장 리서치 에이전트 + 8장 신뢰성 계층)에 9장의 변경 두 가지를 더한 것입니다.

## 책과 다른 점

1. `summarize_costs()` 실행 줄을 `if __name__ == "__main__":` 아래로 옮겼습니다.
2. `write_report` 조각은 프롬프트를 만드는 부분이 빠져 있고 끝이 `...`입니다. 7장 `write_report`의 프롬프트 생성과 `return`으로 채웠습니다. 책의 조각대로 이 버전은 `call_llm`에 `trace_id`를 넘기지 않습니다(8장 버전과 다른 점).
3. `run_tool`: 책은 "7장의 도구 분기처럼 이름에 따라 실제 함수를 호출하는 디스패처라고 가정"합니다. 7장의 분기를 그대로 옮겨 `security.py`에 두었습니다.
4. 책은 9장 코드가 8장 코드와 같은 파일에 있다고 보므로 `json`을 따로 import하지 않습니다. `cost.py`에 `import json`과 `from reliability import call_llm`을 보충했습니다.

보충한 곳은 코드에 `# [예제 보충]`으로 표시했습니다.

## 실행

```bash
uv sync
echo "OPENAI_API_KEY=sk-..." > .env
uv run research_agent.py  # 조사에는 luna, 보고서 작성에는 terra를 씁니다. 기록은 llm_calls.jsonl
uv run cost.py            # 현재 디렉터리의 llm_calls.jsonl을 집계: "호출 수: N, 총비용: $X"
```

`security.py`의 함수들은 따로 실행하는 프로그램이 아니라 가져다 쓰는 부품입니다. `run_in_sandbox`는 Docker가 설치되어 있고 데몬이 떠 있어야 합니다.
