"""4장 첫 번째 구현: 전부 LLM에게 맡기기.

LLM이 보드를 만들고 verify_puzzle 도구로 검증하며, 실패하면 피드백을 받아 다시 만듭니다.
책의 설명처럼 이 구현은 대부분 실패합니다(두 번째 구현은 generator_v2.py).

실행: python generator_v1.py  (.env에 OPENAI_API_KEY 필요)
"""


import json
from openai import OpenAI
from dotenv import load_dotenv  # [예제 보충] '환경 설정은 3장과 같이 load_dotenv로 불러온다고 가정합니다'

from queens_verify import verify_puzzle  # [예제 보충] 앞 절의 검증 코드(queens_verify.py)

load_dotenv()  # [예제 보충]

client = OpenAI()

SYSTEM_PROMPT = """당신은 Queens 퍼즐 생성기입니다.
N×N 격자판의 색상 영역을 설계하여 유효한 Queens 퍼즐을 만드세요.

규칙:
- 격자판은 N×N 크기입니다.
- N개의 색상 영역이 있으며 각 영역은 연결되어 있어야 합니다.
- 각 행, 각 열, 각 색상 영역에 정확히 하나의 퀸을 배치할 수 있어야 합니다.
- 어떤 두 퀸도 상하좌우 또는 대각선으로 인접하면 안 됩니다.
- 정답은 정확히 하나여야 합니다.

작업 방식: 보드를 만들면 반드시 verify_puzzle 도구를 호출하여
검증하세요. 직접 유효하다고 판단하지 마세요.

보드는 2차원 배열이며 색상 영역은 1부터 N까지의 정수로 표현합니다.
예시 (5×5):
{"board": [[1,1,2,2,2],[1,3,3,4,2],[1,3,5,4,4],[3,3,5,5,4],[5,5,5,4,4]]}

위 예시는 형식을 보여주기 위한 것입니다. 예시와 똑같은 배치를
그대로 사용하지 마세요.
"""

tools = [
  {
    "type": "function",
    "function": {
      "name": "verify_puzzle",
      "description": "생성된 Queens 퍼즐이 유효한지 검증합니다.",
      "parameters": {
        "type": "object",
        "properties": {
          "board": {
            "type": "array",
            "items": {"type": "array", "items": {"type": "integer"}},
            "description": "색상 영역을 나타내는 2차원 배열"
          }
        },
        "required": ["board"]
      }
    }
  }
]


def generate_queens_puzzle(size=5, max_attempts=10):
  """Queens 퍼즐을 생성합니다."""
  messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": f"{size}×{size} Queens 퍼즐을 만들어주세요."}
  ]

  for attempt in range(max_attempts):
    # LLM에게 퍼즐 생성 요청
    response = client.chat.completions.create(
      model="gpt-5.6-luna",
      messages=messages,
      tools=tools,
      reasoning_effort="none",
      temperature=0.8
    )
    message = response.choices[0].message
    messages.append(message.model_dump())  # SDK 객체를 딕셔너리로 변환

    # 도구 호출 처리
    if message.tool_calls:
      for tool_call in message.tool_calls:
        args = json.loads(tool_call.function.arguments)
        result = verify_puzzle(args["board"])
        messages.append({
          "role": "tool",
          "tool_call_id": tool_call.id,
          "content": json.dumps(result, ensure_ascii=False)
        })

        if result["valid"] and result["unique"]:
          return {
            "board": args["board"],
            "solution": result["solution"],
            "attempts": attempt + 1
          }

        # 검증 실패: 피드백 제공
        feedback = f"검증 실패: {', '.join(result['errors'])}. "
        feedback += "다른 색상 영역 배치로 다시 시도해주세요."
        print(f"[시도 {attempt + 1}] {feedback}")
        messages.append({"role": "user", "content": feedback})
    else:
      # 도구를 호출하지 않고 텍스트로만 답한 경우: 재지시
      messages.append({
        "role": "user",
        "content": "보드를 verify_puzzle 도구로 검증해주세요."
      })

  return None  # max_attempts 초과


# [예제 보충] import할 때 바로 실행되지 않도록 실행 코드를 main 아래로 옮겼습니다.
if __name__ == "__main__":
  result = generate_queens_puzzle(size=5)
  print("성공" if result else "생성 실패")
