"""3장 '방법 1: 프롬프트로 도구 사용하기'. 프롬프트에 도구 목록과 JSON 응답 형식을 설명합니다.

알려진 문제: 도구 결과를 받은 두 번째 응답이 JSON이 아니면, 오류 메시지의 'LLM 응답'으로
두 번째 응답이 아니라 첫 응답(도구 호출 JSON)을 출력합니다.

실행: python step3_prompt_tools.py  (종료: quit)
"""

# agent.py
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from tools import get_current_weather, get_current_time

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat_with_manual_tools():
  """프롬프트 엔지니어링으로 도구를 사용하는 에이전트"""
  messages = []

  # 시스템 프롬프트에 도구와 응답 형식 설명
  system_prompt = """당신은 도구를 사용할 수 있는 에이전트입니다.

사용 가능한 도구:
1. get_current_weather - 지정된 위치의 현재 날씨를 조회합니다
   - 인자: location (문자열) - 도시 이름
2. get_current_time - 현재 시각을 조회합니다
   - 인자: 없음

도구를 사용하려면 다음 JSON 형식으로 응답하세요:
{
  "tool": "도구이름",
  "arguments": {"인자명": "값"}
}

도구를 사용하지 않을 때는:
{
  "response": "사용자에게 전달할 메시지"
}

예시:
사용자: 서울 날씨 알려줘
{"tool": "get_current_weather", "arguments": {"location": "서울"}}

사용자: 안녕?
{"response": "안녕하세요! 무엇을 도와드릴까요?"}
"""

  messages.append({"role": "system", "content": system_prompt})

  print("도구를 사용하는 에이전트입니다. (종료: 'quit')")

  while True:
    user_input = input("\n당신: ")
    if user_input.lower() == "quit":
      break

    messages.append({"role": "user", "content": user_input})

    # LLM 호출
    response = client.chat.completions.create(
      model="gpt-5.6-luna",
      messages=messages
    )

    assistant_message = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_message})

    # JSON 파싱
    try:
      action = json.loads(assistant_message)

      if "tool" in action:
        # 도구 호출
        tool_name = action["tool"]
        arguments = action.get("arguments", {})

        print(f"[도구 호출] {tool_name}({arguments})")

        # 함수 실행
        if tool_name == "get_current_weather":
          result = get_current_weather(**arguments)
        elif tool_name == "get_current_time":
          result = get_current_time()
        else:
          result = f"알 수 없는 도구: {tool_name}"

        print(f"[도구 결과] {result}")

        # 결과를 메모리에 추가
        messages.append({"role": "user", "content": f"도구 실행 결과: {result}"})

        # LLM에게 다시 물어보기
        second_response = client.chat.completions.create(
          model="gpt-5.6-luna",
          messages=messages
        )

        final_message_content = second_response.choices[0].message.content
        final_action = json.loads(final_message_content)

        if "response" in final_action:
          print(f"에이전트: {final_action['response']}")
          messages.append({"role": "assistant", "content": final_message_content})
        else:
          print(f"[경고] 예상한 형식이 아닙니다: {final_message_content}")

      elif "response" in action:
        # 도구 호출 없이 바로 응답
        print(f"에이전트: {action['response']}")

    except json.JSONDecodeError as e:
      print(f"[오류] JSON 파싱 실패: {e}")
      print(f"LLM 응답: {assistant_message}")

if __name__ == "__main__":
  chat_with_manual_tools()
