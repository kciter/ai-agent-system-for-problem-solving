"""3장 'ReAct 패턴'. 생각(thought) → 행동(action) → 관찰(observation)을 답이 나올 때까지 반복합니다.

실행: python step5_react.py  (종료: quit)
"""

# [예제 보충] 책에서는 앞 단계의 agent.py에 이어서 작성합니다. 그 설정 부분을 그대로 가져왔습니다.
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from tools import get_current_weather, get_current_time

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def react_agent():
  """ReAct 패턴을 사용하는 에이전트"""
  messages = []

  system_prompt = """당신은 ReAct 패턴을 사용하는 에이전트입니다.

사용 가능한 도구:
- get_current_weather(location): 지정된 도시의 현재 날씨를 조회합니다
- get_current_time(): 현재 시각을 조회합니다

단계마다 다음 JSON 형식으로 응답하세요.
한 번의 응답에는 JSON 객체 하나만 출력하세요:

{
  "thought": "현재 상황 분석 및 다음 행동 계획",
  "action": {
    "tool": "도구이름",
    "arguments": {"인자명": "값"}
  }
}

또는 최종 답변:
{
  "thought": "최종 분석",
  "answer": "사용자에게 전달할 답변"
}

예시:
사용자: 서울과 부산 중 어디가 더 따뜻해?

1단계:
{
  "thought": "서울과 부산의 날씨를 비교하려고 한다. 먼저 서울의 날씨를 확인해야 한다.",
  "action": {
    "tool": "get_current_weather",
    "arguments": {"location": "서울"}
  }
}

2단계:
{
  "thought": "서울은 18도이다. 이제 부산의 날씨도 확인해야 한다.",
  "action": {
    "tool": "get_current_weather",
    "arguments": {"location": "부산"}
  }
}

3단계:
{
  "thought": "서울은 18도, 부산은 22도이다. 부산이 4도 더 따뜻하다.",
  "answer": "부산이 서울보다 4도 더 따뜻합니다. 서울은 18도, 부산은 22도입니다."
}
"""

  messages.append({"role": "system", "content": system_prompt})

  print("ReAct 에이전트입니다. (종료: 'quit')")

  while True:
    user_input = input("\n당신: ")
    if user_input.lower() == "quit":
      break

    messages.append({"role": "user", "content": user_input})

    max_iterations = 10  # 무한 루프 방지

    for i in range(max_iterations):
      response = client.chat.completions.create(
        model="gpt-5.6-luna",
        messages=messages
      )

      assistant_message = response.choices[0].message.content
      messages.append({"role": "assistant", "content": assistant_message})

      try:
        step = json.loads(assistant_message)

        print(f"\n[단계 {i+1}]")
        print(f"Thought: {step['thought']}")

        if "answer" in step:
          # 최종 답변
          print(f"\n에이전트: {step['answer']}")
          break
        elif "action" in step:
          # 도구 실행
          action = step["action"]
          tool_name = action["tool"]
          arguments = action.get("arguments", {})

          print(f"Action: {tool_name}({arguments})")

          # 도구 실행
          if tool_name == "get_current_weather":
            result = get_current_weather(**arguments)
          elif tool_name == "get_current_time":
            result = get_current_time()
          else:
            result = f"알 수 없는 도구: {tool_name}"

          # 결과를 Observation으로 추가
          observation = f"Observation: {result}"
          messages.append({"role": "user", "content": observation})
          print(observation)

      except (json.JSONDecodeError, KeyError) as e:
        print(f"\n[오류] 응답 처리 실패: {e}")
        print(f"LLM 응답: {assistant_message}")
        break

if __name__ == "__main__":
  react_agent()
