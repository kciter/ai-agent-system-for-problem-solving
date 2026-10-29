"""4장 두 번째 구현: 역할을 다시 나누다.

정답 배치는 코드(난수 + 백트래킹)가 만들고, LLM은 추론 모드로 색상 영역만 디자인합니다.
검증은 도구가 아니라 루프 안에서 코드가 직접 호출합니다.

실행: python generator_v2.py  (.env에 OPENAI_API_KEY 필요)
"""


# [예제 보충] 첫 번째 구현(generator_v1.py)과 같은 설정입니다. 책에서는 같은 파일에 이어서 씁니다.
import json  # [예제 보충]
from dotenv import load_dotenv  # [예제 보충]
from openai import OpenAI  # [예제 보충]

from queens_verify import verify_puzzle  # [예제 보충] 앞 절의 검증 코드(queens_verify.py)

load_dotenv()  # [예제 보충]
client = OpenAI()  # [예제 보충]


import random

def generate_solution(n):
  """백트래킹으로 무작위 유효 퀸 배치를 생성합니다."""
  def backtrack(row, placed):
    if row == n:
      return list(placed)
    candidates = list(range(n))
    random.shuffle(candidates)
    for col in candidates:
      if all(c != col and not (abs(r - row) <= 1 and abs(c - col) <= 1)
             for r, c in placed):
        placed.append((row, col))
        result = backtrack(row + 1, placed)
        if result:
          return result
        placed.pop()
    return None
  return backtrack(0, [])


DESIGNER_PROMPT = """당신은 Queens 퍼즐의 색상 영역 디자이너입니다.
정답 퀸 배치가 주어지면, 그 배치가 유일한 정답이 되도록
N×N 격자판을 N개의 색상 영역으로 나눕니다.

규칙:
- 색상 영역은 1부터 N까지의 정수로만 표현합니다.
- 각 색상 영역은 상하좌우로 이어진 한 덩어리여야 합니다.
- 각 색상 영역은 주어진 퀸 중 정확히 하나를 포함해야 합니다.
- 각 색상 영역은 최소 2칸 이상이어야 합니다.
- 영역들이 격자판 전체를 빈틈없이 채워야 합니다.
- 주어진 배치 외의 다른 퀸 배치는 정답이 되면 안 됩니다.

응답은 다음 JSON 형식으로만 하세요:
{"board": [[...], [...], ...]}
"""


def verify_design(board, solution):
  """디자인된 보드를 검증합니다. verify_puzzle에 세 가지 검사를 더합니다."""
  n = len(board)
  cells = [cell for row in board for cell in row]
  if not all(isinstance(cell, int) and 1 <= cell <= n for cell in cells):
    return [f"색상 값은 1부터 {n}까지의 정수여야 합니다."]
  if any(cells.count(color) < 2 for color in set(cells)):
    return ["한 칸짜리 색상 영역이 있습니다. 각 영역은 최소 2칸이어야 합니다."]
  result = verify_puzzle(board)
  if not (result["valid"] and result["unique"]):
    return result["errors"]
  if sorted(result["solution"]) != sorted(solution):
    return [f"주어진 배치가 아니라 {result['solution']}가 정답이 되었습니다."]
  return []


def generate_queens_puzzle_v2(size=5, max_attempts=5):
  """정답 배치는 코드가 만들고, 영역 디자인은 LLM이 맡습니다."""
  solution = generate_solution(size)
  messages = [
    {"role": "system", "content": DESIGNER_PROMPT},
    {"role": "user", "content":
     f"{size}×{size} 격자판입니다. 다음 정답 배치를 기준으로 "
     f"색상 영역을 설계해주세요: {solution}"}
  ]

  for attempt in range(max_attempts):
    response = client.chat.completions.create(
      model="gpt-5.6-luna",
      messages=messages,
      response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content
    messages.append({"role": "assistant", "content": content})

    try:
      board = json.loads(content).get("board")
      errors = verify_design(board, solution) if board else ["board 키가 없습니다."]
    except json.JSONDecodeError:
      errors = ["응답이 유효한 JSON이 아닙니다."]

    if not errors:
      return {"board": board, "solution": solution, "attempts": attempt + 1}

    print(f"[시도 {attempt + 1}] 검증 실패: {', '.join(errors)}")
    messages.append({"role": "user", "content":
                     f"검증 실패: {', '.join(errors)} 다시 시도해주세요."})

  return None


# [예제 보충] import할 때 바로 실행되지 않도록 실행 코드를 main 아래로 옮겼습니다.
if __name__ == "__main__":
  result = generate_queens_puzzle_v2(size=5)
  if result:
    print(f"퍼즐 생성 완료 (시도 횟수: {result['attempts']})")
    for row in result["board"]:
      print(row)
    print(f"정답: {result['solution']}")
