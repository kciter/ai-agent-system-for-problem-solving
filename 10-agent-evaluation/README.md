# 10장 에이전트 평가

리서치 에이전트의 결과(루브릭 채점)와 궤적(인용 검증, 조사 성실성)을 함께 재는 평가 하네스와, 회귀 비교, 채점자 검증입니다.

## 파일

| 파일 | 내용 | 책의 위치 |
|---|---|---|
| `evaluation.py` | `validate_judge`, `run_research_traced`, `clean_url`, `check_citations`, `check_effort`, `RUBRIC_FORMAT`, `judge_report`, `EVAL_TOPICS`, `run_eval_suite`, `rubric_avg`, `compare_runs` | '채점자를 채점하기'부터 '회귀: 변경 앞의 관문'까지 |
| `research_agent.py` | 평가 대상인 리서치 에이전트(7장 + 8장 신뢰성 계층 + 9장 모델 선택·경계 표시) | 7~9장 |
| `reliability.py` | 8장 신뢰성 계층(`call_llm`과 로그) | 8장 |

앞 장에서 가져온 코드:

- `reliability.py`는 `08-reliability/reliability.py`와, `research_agent.py`는 `09-cost-and-security`의 같은 이름 파일과 같습니다.
- 그래서 `run_eval_suite`의 보고서는 9장 `write_report`(`MODELS["complex"]`, 즉 gpt-5.6-terra)가 쓰고, `validate_judge`가 쓰는 채점자는 8장 `evaluate_report`입니다.

## 책과 다른 점

1. `run_research_traced`: 책은 뼈대만 보여주고 "루프 본문은 7장의 run_research와 같고, 도구를 실행한 지점에 아래 한 줄이 추가됩니다"라고 합니다. 독자의 코드는 8장에서 `call_llm`으로 바뀌었으므로, 8장 `run_research`의 본문을 채우고 도구 실행 직후에 `trajectory.append((name, args, result))`를 넣었습니다. 조사 노트는 `notes`에 담아 책처럼 `return notes, trajectory`로 돌려줍니다.
2. 책에 없는 실행 줄 `run_eval_suite()`를 `if __name__ == "__main__":` 아래에 보충했습니다.
3. 여러 파일로 나누면서 필요한 import(`json`, `uuid`, 앞 장 함수들)를 보충했습니다.

보충한 곳은 코드에 `# [예제 보충]`으로 표시했습니다.

## 실행

```bash
uv sync
echo "OPENAI_API_KEY=sk-..." > .env
uv run evaluation.py      # 평가 주제 3개로 조사·작성·채점
```
