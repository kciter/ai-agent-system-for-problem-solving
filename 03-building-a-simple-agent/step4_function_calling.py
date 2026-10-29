"""3장 '방법 2: 오픈AI가 제공하는 Function Calling'과 '도구를 사용하는 에이전트'.

도구를 JSON 스키마로 tools 파라미터에 넘기고, 응답의 tool_calls를 실행합니다.

알려진 문제: 도구 결과를 받은 두 번째 응답이 또 도구 호출이면 그 호출을 실행하지 않고
"에이전트: None"을 출력합니다.

실행: python step4_function_calling.py  (종료: quit)
"""

# agent.py
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from tools import get_current_weather, get_current_time

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 도구를 JSON 스키마로 정의
tools = [
  {
    "type": "function",
    "function": {
      "name": "get_current_weather",
      "description": "지정된 위치의 현재 날씨를 조회합니다.",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "도시 이름 (예: 서울, 부산)"
          }
        },
        "required": ["location"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "get_current_time",
      "description": "현재 시각을 조회합니다.",
      "parameters": {
        "type": "object",
        "properties": {}
      }
    }
  }
]

def chat_with_tools():
  """도구를 사용할 수 있는 에이전트"""
  messages = []

  print("도구를 사용하는 에이전트입니다. (종료: 'quit')")

  while True:
    user_input = input("\n당신: ")
    if user_input.lower() == "quit":
      break

    messages.append({"role": "user", "content": user_input})

    # LLM 호출 (도구 목록 포함)
    response = client.chat.completions.create(
      model="gpt-5.6-luna",
      messages=messages,
      tools=tools,  # 사용 가능한 도구 전달
      reasoning_effort="none"
    )

    response_message = response.choices[0].message

    # LLM이 도구를 호출하려고 하는가?
    if response_message.tool_calls:
      # 도구 호출 정보를 메모리에 추가 (SDK 객체를 딕셔너리로 변환)
      messages.append(response_message.model_dump())

      # 각 도구 호출 처리
      for tool_call in response_message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        print(f"[도구 호출] {function_name}({arguments})")

        # 실제 함수 실행
        if function_name == "get_current_weather":
          result = get_current_weather(**arguments)
        elif function_name == "get_current_time":
          result = get_current_time()
        else:
          result = "알 수 없는 함수입니다."

        print(f"[도구 결과] {result}")

        # 도구 실행 결과를 메모리에 추가
        messages.append({
          "role": "tool",
          "tool_call_id": tool_call.id,
          "content": result
        })

      # 도구 결과를 받은 LLM에게 다시 물어보기
      second_response = client.chat.completions.create(
        model="gpt-5.6-luna",
        messages=messages,
        tools=tools,
        reasoning_effort="none"
      )

      assistant_message = second_response.choices[0].message.content
      messages.append({"role": "assistant", "content": assistant_message})
      print(f"에이전트: {assistant_message}")
    else:
      # 도구 호출 없이 바로 응답
      assistant_message = response_message.content
      messages.append({"role": "assistant", "content": assistant_message})
      print(f"에이전트: {assistant_message}")

if __name__ == "__main__":
  chat_with_tools()
