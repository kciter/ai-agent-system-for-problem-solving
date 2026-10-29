"""3장 '출발점: LLM만 사용'. 메모리 없이 LLM을 두 번 호출합니다.

두 호출이 서로 독립적이라 두 번째 질문("내 이름이 뭐였지?")에 답하지 못합니다.
실행: python step1_call_llm.py  (.env에 OPENAI_API_KEY 필요)
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_llm(prompt: str) -> str:
  """LLM에게 한 번 질문하고 응답을 받습니다."""
  response = client.chat.completions.create(
    model="gpt-5.6-luna",
    messages=[{"role": "user", "content": prompt}]
  )
  return response.choices[0].message.content

if __name__ == "__main__":  # [예제 보충] import할 때 바로 실행되지 않도록
  # 테스트
  print(call_llm("안녕? 내 이름은 철수야"))
  print(call_llm("내 이름이 뭐였지?"))
