"""3장 'Plan-and-Execute 패턴'. 먼저 전체 계획을 세우고, 계획에 따라 한 단계씩 실행합니다.

실행: python step6_plan_and_execute.py  (작업을 하나 입력하면 계획과 실행 과정을 출력하고 끝납니다)
"""

# [예제 보충] 책에서는 앞 단계의 agent.py에 이어서 작성합니다. 그 설정 부분을 그대로 가져왔습니다.
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from tools import get_current_weather, get_current_time

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def plan_and_execute_agent():
  """Plan-and-Execute 패턴을 사용하는 에이전트"""
  messages = []

  system_prompt = """당신은 Plan-and-Execute 에이전트입니다.

사용 가능한 도구:
- get_current_weather(location): 지정된 도시의 현재 날씨를 조회합니다
- get_current_time(): 현재 시각을 조회합니다

한 번의 응답에는 JSON 객체 하나만 출력하세요.

1단계: 작업을 받으면 먼저 전체 계획을 JSON 형식으로 세우세요.
{
  "plan": [
    "첫 번째 단계",
    "두 번째 단계",
    "세 번째 단계"
  ]
}

2단계: 계획의 각 단계를 실행합니다.
{
  "step": 1,
  "action": {
    "tool": "도구이름",
    "arguments": {"인자명": "값"}
  }
}

또는 도구 없이:
{
  "step": 1,
  "description": "수행한 작업 설명"
}

모든 단계가 완료되면:
{
  "answer": "최종 답변"
}
"""

  messages.append({"role": "system", "content": system_prompt})

  user_input = input("작업을 입력하세요: ")
  messages.append({"role": "user", "content": user_input})

  # 1단계: 계획 수립
  response = client.chat.completions.create(
    model="gpt-5.6-luna",
    messages=messages
  )

  plan_content = response.choices[0].message.content
  messages.append({"role": "assistant", "content": plan_content})

  try:
    plan_data = json.loads(plan_content)
    print("\n=== 계획 ===")
    for i, step in enumerate(plan_data["plan"], 1):
      print(f"{i}. {step}")

    # 2단계: 실행
    max_iterations = 10
    for i in range(max_iterations):
      messages.append({"role": "user", "content": "다음 단계를 실행하세요."})

      response = client.chat.completions.create(
        model="gpt-5.6-luna",
        messages=messages
      )

      step_content = response.choices[0].message.content
      messages.append({"role": "assistant", "content": step_content})

      step_data = json.loads(step_content)

      if "answer" in step_data:
        print(f"\n=== 최종 답변 ===")
        print(step_data["answer"])
        break
      elif "action" in step_data:
        action = step_data["action"]
        tool_name = action["tool"]
        arguments = action.get("arguments", {})

        print(f"\n[단계 {step_data['step']}] {tool_name}({arguments})")

        # 도구 실행
        if tool_name == "get_current_weather":
          result = get_current_weather(**arguments)
        elif tool_name == "get_current_time":
          result = get_current_time()
        else:
          result = f"알 수 없는 도구: {tool_name}"

        print(f"결과: {result}")
        messages.append({"role": "user", "content": f"결과: {result}"})
      elif "description" in step_data:
        print(f"\n[단계 {step_data['step']}] {step_data['description']}")

  except (json.JSONDecodeError, KeyError) as e:
    print(f"[오류] 응답 처리 실패: {e}")

if __name__ == "__main__":
  plan_and_execute_agent()
