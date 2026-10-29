"""3장 '메모리 추가하기'. 대화 히스토리(messages)를 매번 전달해 이전 대화를 기억합니다.

실행: python step2_memory.py  (종료: quit)
"""

# [예제 보충] 책에서는 앞 단계의 agent.py에 이어서 작성합니다. 그 설정 부분을 그대로 가져왔습니다.
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat_with_memory():
  """메모리를 사용하여 대화 히스토리를 기억합니다."""
  messages = []  # 메모리: 대화 히스토리 저장

  print("대화를 시작합니다. (종료: 'quit')")

  while True:
    user_input = input("\n당신: ")
    if user_input.lower() == "quit":
      break

    # 1. 사용자 메시지를 메모리에 추가
    messages.append({"role": "user", "content": user_input})

    # 2. 메모리(전체 히스토리)를 LLM에 전달
    response = client.chat.completions.create(
      model="gpt-5.6-luna",
      messages=messages  # 전체 대화 히스토리 전달
    )

    assistant_message = response.choices[0].message.content

    # 3. LLM 응답을 메모리에 추가
    messages.append({"role": "assistant", "content": assistant_message})

    print(f"에이전트: {assistant_message}")

if __name__ == "__main__":
  chat_with_memory()
