# 3장 간단한 AI 에이전트 만들어보기

LLM 호출 한 줄에서 시작해 메모리, 도구(프롬프트 방식과 Function Calling), 계획(ReAct, Plan-and-Execute)을 차례로 얹는 3장의 코드입니다. 책은 `agent.py` 하나를 단계마다 고쳐 쓰지만, 여기서는 단계마다 파일을 나눠 모든 단계를 따로 실행할 수 있게 했습니다. `tools.py`는 책과 같은 이름입니다.

## 파일

| 파일 | 내용 | 책의 위치 |
|---|---|---|
| `agent.py` | 기본 설정(`load_dotenv`, `client`, `main`) | 3장 '기본 설정 코드' |
| `step1_call_llm.py` | `call_llm`: 메모리 없이 LLM만 호출 | 3장 '출발점: LLM만 사용' |
| `step2_memory.py` | `chat_with_memory`: 대화 히스토리를 매번 전달 | 3장 '메모리 추가하기' |
| `tools.py` | `get_current_weather`(임의의 값), `get_current_time` | 3장 '도구 정의하기' |
| `step3_prompt_tools.py` | `chat_with_manual_tools`: 프롬프트로 도구 사용 | 3장 '방법 1: 프롬프트로 도구 사용하기' |
| `step4_function_calling.py` | 도구 스키마 `tools`, `chat_with_tools`: 네이티브 Function Calling | 3장 '방법 2: 오픈AI가 제공하는 Function Calling', '도구를 사용하는 에이전트' |
| `step5_react.py` | `react_agent` | 3장 'ReAct 패턴' |
| `step6_plan_and_execute.py` | `plan_and_execute_agent` | 3장 'Plan-and-Execute 패턴' |

## 책과 다른 점

- 단계별 파일: 책은 `agent.py`를 고쳐 가며 쓰고, 단계에 따라 앞 단계의 설정 부분(import, `load_dotenv()`, `client`)에 이어서 작성합니다. 설정 부분이 없는 조각(`step2_memory.py`, `step5_react.py`, `step6_plan_and_execute.py`)에는 앞 단계의 설정 줄을 그대로 가져와 붙였습니다. `step3_prompt_tools.py`와 `step4_function_calling.py`는 책의 코드에 설정이 들어 있어서 첫 줄의 `# agent.py` 주석까지 책 그대로입니다.
- `step1_call_llm.py`: 마지막 두 줄(`# 테스트` 아래의 `print(call_llm(...))`)을 `if __name__ == "__main__":` 아래로 옮겼습니다. 다른 파일에서 import할 때 API가 호출되지 않게 하기 위해서입니다. 나머지 단계의 `if __name__ == "__main__":`은 책에 원래 있습니다.
- 넣지 않은 코드: 실행하는 프로그램이 아니라 개념을 보여 주려고 넣은 코드 조각은 예제에서 뺐습니다. '메모리 추가하기'의 메모리 추적 조각과 토큰 사용량 한 줄, '메모리만으로는 부족하다'의 시스템 프롬프트 메시지, '두 방식의 비교'의 응답 구조 비교 조각, 'JSON 응답을 더 안정적으로'와 '만들어보며 느낀 특징과 한계'의 호출 조각입니다.

덧붙인 줄에는 모두 `# [예제 보충]` 표시가 있습니다.

## 실행

```bash
uv sync
echo "OPENAI_API_KEY=sk-..." > .env
uv run agent.py                   # "AI 에이전트 시작"
uv run step1_call_llm.py
uv run step2_memory.py            # 대화형(종료: quit)
uv run step3_prompt_tools.py      # 대화형(종료: quit)
uv run step4_function_calling.py  # 대화형(종료: quit)
uv run step5_react.py             # 대화형(종료: quit)
uv run step6_plan_and_execute.py  # 작업 하나를 입력하면 계획과 실행 과정을 출력하고 끝납니다
```

`tools.py`의 날씨는 실습용 임의의 값이라 실행할 때마다 다릅니다.
