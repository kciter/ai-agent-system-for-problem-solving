# 8장 신뢰성 있는 에이전트 만들기

LLM 호출에 재시도, 타임아웃, 폴백, 형식 검증, LLM 평가자, 로깅을 더하고, 6장 튜터와 7장 리서치 에이전트에 적용합니다.

## 파일

| 파일 | 내용 | 책의 위치 |
|---|---|---|
| `reliability.py` | 클라이언트(`max_retries=0` 다음에 최종 설정 `timeout=30.0, max_retries=0`), `RETRYABLE_ERRORS`, `call_with_retry`, `chat_with_fallback`, `get_json_response`, `call_llm`, `write_log` | '재시도 전략', '타임아웃과 폴백', '형식 검증'의 첫 코드, '모니터링과 로깅' |
| `tutor_eval.py` | 6장 `SYSTEM_PROMPT`, `TUTOR_RESPONSE_FORMAT`과 요청 예, 평가 세트 `eval_cases`와 `run_eval` | '형식 검증', '일관성과 재현성' |
| `research_agent.py` | 7장 리서치 에이전트의 호출을 `call_llm`으로 바꾼 것, `EVALUATOR_FORMAT`, `evaluate_report`, 재작성 루프가 있는 `research_agent` | '내용 검증', '적용: 리서치 에이전트에 신뢰성 더하기' |

앞 장에서 가져온 코드:

- `research_agent.py`의 `search_web`, `read_webpage`, 도구 정의, `RESEARCH_SYSTEM_PROMPT`, `run_research`, `write_report`는 7장 예제(`07-research-agent/research_agent.py`)에서 가져와 8장 본문대로 고쳤습니다.
- `tutor_eval.py`의 `SYSTEM_PROMPT`는 6장 '구현: 튜터 에이전트'의 것입니다.

## 책과 다른 점

1. 실행 줄을 `if __name__ == "__main__":` 아래로 옮겼습니다. `reliability.py`의 '사용 예'(받은 응답을 출력하는 `print` 한 줄을 보충), `tutor_eval.py`의 `run_eval()`, `research_agent.py`의 7장 실행 줄입니다.
2. 클라이언트: 책은 처음에 `OpenAI(max_retries=0)`를 만들고, 뒤에서 "이후 예제들은 모두 이 클라이언트를 사용한다고 가정합니다"라며 `OpenAI(timeout=30.0, max_retries=0)`를 보여줍니다. `reliability.py`도 같은 순서로 두 번 만들어, 실제로는 뒤의 것을 씁니다.
3. `messages`가 이미 있다고 보고 바로 요청을 보내는 Structured Outputs 요청은 `get_structured_tutor_response(messages)` 함수로 감쌌습니다.
4. 본문에만 있고 코드로는 보여주지 않은 부분을 채웠습니다(코드에 `# [예제 보충]` 표시).
   - `load_dotenv()`로 `.env`의 API 키를 읽습니다(3장과 같은 방식).
   - 7장의 `client = OpenAI()` 대신 `reliability.py`의 클라이언트를 `call_llm`이 씁니다.
   - '적용' 절대로 `run_research`, `write_report`, `evaluate_report`의 호출을 `call_llm(trace_id=trace_id, ...)`으로 바꾸고, 각 함수가 시작할 때 `trace_id = str(uuid.uuid4())`를 만듭니다. 책은 "uuid.uuid4() 같은 방법"이라고만 했는데, UUID 객체를 그대로 넘기면 `write_log`가 기록하지 못하고 예외가 나서 프로그램이 멈춥니다. 그래서 문자열로 바꿨습니다.
5. 넣지 않은 코드: 실행하는 프로그램이 아니라 설명용으로 넣은 조각은 예제에서 뺐습니다. '재시도 전략'과 '타임아웃과 폴백'의 한 줄짜리 클라이언트 설정 예시 두 개(`max_retries=3`, `timeout=30.0`), 교체 전의 7장 코드를 다시 보여주는 블록(`# 7장의 코드`)입니다.

## 실행

```bash
uv sync
echo "OPENAI_API_KEY=sk-..." > .env
uv run reliability.py       # call_with_retry로 한 번 호출
uv run tutor_eval.py        # 튜터 평가 세트 6문장
uv run research_agent.py    # 조사 → 작성 → 검증. 호출 기록은 llm_calls.jsonl에 쌓입니다
```
