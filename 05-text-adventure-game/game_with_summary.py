"""5장 텍스트 어드벤처 게임 + 대화 히스토리 요약.

game.py에 '세계관 일관성 유지' 절의 summarize_history를 더하고,
메인 루프에서 메시지가 20개를 넘으면 요약하도록 연결한 판입니다.

실행: python game_with_summary.py  (환경 변수 OPENAI_API_KEY 필요)
"""


initial_state = {
  "day": 1,
  "time": "아침",
  "health": 100,
  "hunger": 80,
  "thirst": 80,
  "inventory": [],
  "location": "해변",
  "game_over": False,
  "game_clear": False
}


SYSTEM_PROMPT = """당신은 텍스트 어드벤처 게임 "무인도에서 살아남기"의 게임 마스터입니다.

## 배경
플레이어는 비행기 사고로 무인도에 조난되었습니다. 아무것도 가진 것 없이 해변에서
시작합니다. 목표는 7일 이상 생존한 뒤 구조 신호를 보내 탈출하는 것입니다.

## 세계관
- 무인도에는 해변, 숲, 동굴, 절벽, 강가 등의 장소가 있습니다.
- 자연에서 재료를 모아 도구를 만들 수 있습니다.
- 날씨는 변할 수 있으며 행동에 영향을 줍니다.
- 위험한 동물이 있을 수 있습니다.

## 스탯 규칙
- health (체력): 부상이나 위험으로 감소. 0이면 게임 오버.
- hunger (허기): 행동마다 5 감소. 음식을 먹으면 회복.
  0이면 행동마다 체력 10 감소.
- thirst (갈증): 행동마다 7 감소. 물을 마시면 회복.
  0이면 행동마다 체력 10 감소.
- 모든 스탯은 0~100 범위입니다.

## 진행 규칙
- 잠을 자면 다음 날로 넘어갑니다. 시간은 아침이 됩니다.
- 잠을 자면 체력이 20 회복됩니다 (100을 넘지 않습니다).
- 확률이 필요한 상황에서는 반드시 roll_dice 도구를 사용하세요.
  예: 사냥, 낚시, 위험한 탐험 등
- 7일차 이후 불을 피울 수 있는 상태에서 구조 신호를 보내면 게임 클리어입니다.
  구조 신호를 보내려면 인벤토리에 "횃불" 또는 "모닥불" 관련 아이템이 필요합니다.

## 입력 검증
플레이어가 세계관에 맞지 않는 행동을 시도할 수 있습니다.
- 마법, 초능력, 텔레포트 등 현실에 존재하지 않는 능력은 사용할 수 없습니다.
- 맨손으로 나무를 부수는 등 물리적으로 불가능한 행동도 불가합니다.
- 이런 시도가 있을 경우, 행동이 실패했음을 자연스럽게 묘사하고
  state_changes는 비워두세요. 기본 소모는 시스템이 적용합니다.
- 절대로 세계관을 벗어나는 결과를 만들어내지 마세요.

## 응답 형식
반드시 다음 JSON 형식으로 응답하세요.

{"narrative": "상황 묘사 텍스트",
 "state_changes": {"health": 변화량, "hunger": 변화량, "thirst": 변화량},
 "add_items": ["획득한 아이템"],
 "remove_items": ["소모된 아이템"],
 "location": "현재 장소",
 "time": "아침/낮/저녁/밤",
 "next_day": false,
 "game_over": false,
 "game_clear": false}

state_changes의 값은 행동이 만든 변화량입니다. 감소는 음수, 증가는
양수로 표현합니다. 매 행동의 기본 소모(hunger -5, thirst -7)는
시스템이 자동으로 적용하므로 state_changes에 포함하지 마세요.
예: 물을 마시면 thirst의 변화량을 +30 정도로 설정합니다.
"""


import json
import copy

def parse_response(response_text):
  """LLM 응답에서 JSON을 추출합니다."""
  text = response_text.strip()
  # JSON 블록 추출
  if "```json" in text:
    start = text.index("```json") + 7
    end = text.index("```", start)
    text = text[start:end].strip()
  elif "```" in text:
    start = text.index("```") + 3
    end = text.index("```", start)
    text = text[start:end].strip()

  return json.loads(text)

def apply_state_changes(state, response_data):
  """LLM 응답을 기반으로 게임 상태를 업데이트합니다."""
  new_state = copy.deepcopy(state)

  # 매 행동의 기본 소모를 코드가 확정적으로 적용
  new_state["hunger"] -= 5
  new_state["thirst"] -= 7

  # 행동의 효과 적용
  changes = response_data.get("state_changes", {})
  new_state["health"] += changes.get("health", 0)
  new_state["hunger"] += changes.get("hunger", 0)
  new_state["thirst"] += changes.get("thirst", 0)

  # 허기/갈증이 0이면 체력 추가 감소
  if new_state["hunger"] <= 0:
    new_state["health"] -= 10
  if new_state["thirst"] <= 0:
    new_state["health"] -= 10

  # 스탯 범위 제한 (0~100)
  for key in ["health", "hunger", "thirst"]:
    new_state[key] = max(0, min(100, new_state[key]))

  # 아이템 관리
  for item in response_data.get("add_items", []):
    if item and item not in new_state["inventory"]:
      new_state["inventory"].append(item)
  for item in response_data.get("remove_items", []):
    if item in new_state["inventory"]:
      new_state["inventory"].remove(item)

  # 장소, 시간 업데이트
  if response_data.get("location"):
    new_state["location"] = response_data["location"]
  if response_data.get("time"):
    new_state["time"] = response_data["time"]

  # 게임 오버 판정 (다음 날 회복을 적용하기 전 기준)
  if new_state["health"] <= 0:
    new_state["game_over"] = True

  # 다음 날
  if response_data.get("next_day") and not new_state["game_over"]:
    new_state["day"] += 1
    new_state["time"] = "아침"
    new_state["health"] = min(100, new_state["health"] + 20)

  # 게임 클리어도 코드가 조건을 확인 (7일차 이상 + 불 관련 아이템)
  if response_data.get("game_clear"):
    has_fire = any("횃불" in item or "모닥불" in item
                   for item in new_state["inventory"])
    if new_state["day"] >= 7 and has_fire:
      new_state["game_clear"] = True

  return new_state

def display_status(state):
  """현재 상태를 화면에 표시합니다."""
  print(f"\n--- {state['day']}일차 {state['time']} | {state['location']} ---")
  print(f"체력: {state['health']}  "
        f"허기: {state['hunger']}  "
        f"갈증: {state['thirst']}")
  if state["inventory"]:
    print(f"인벤토리: {', '.join(state['inventory'])}")
  print()


import random

def roll_dice(sides, difficulty):
  """주사위를 굴려 성공 여부를 판정합니다.

  Args:
    sides: 주사위의 면 수 (예: 6이면 1~6)
    difficulty: 성공에 필요한 최소 값

  Returns:
    {"roll": 결과값, "success": 성공여부, "sides": 면수, "difficulty": 난이도}
  """
  result = random.randint(1, sides)
  return {
    "roll": result,
    "success": result >= difficulty,
    "sides": sides,
    "difficulty": difficulty
  }

tools = [
  {
    "type": "function",
    "function": {
      "name": "roll_dice",
      "description": "확률 판정이 필요할 때 주사위를 굴립니다. "
                     "사냥, 낚시, 위험한 탐험 등 성공/실패가 "
                     "확률에 의존하는 상황에서 사용합니다.",
      "parameters": {
        "type": "object",
        "properties": {
          "sides": {
            "type": "integer",
            "description": "주사위의 면 수 (예: 6이면 1~6)"
          },
          "difficulty": {
            "type": "integer",
            "description": "성공에 필요한 최소 값"
          }
        },
        "required": ["sides", "difficulty"]
      }
    }
  }
]


from openai import OpenAI
from dotenv import load_dotenv  # [예제 보충] 3장처럼 .env에서 API 키를 읽습니다.

load_dotenv()  # [예제 보충]
client = OpenAI()

def handle_tool_calls(message):
  """도구 호출을 처리하고 결과를 반환합니다."""
  results = []
  for tool_call in message.tool_calls:
    args = json.loads(tool_call.function.arguments)
    if tool_call.function.name == "roll_dice":
      result = roll_dice(args["sides"], args["difficulty"])
    else:
      result = {"error": "알 수 없는 도구"}
    results.append({
      "role": "tool",
      "tool_call_id": tool_call.id,
      "content": json.dumps(result, ensure_ascii=False)
    })
  return results


def summarize_history(messages, client, keep_recent=6):
  """오래된 대화 히스토리를 요약합니다.

  Args:
    messages: 전체 메시지 리스트
    client: OpenAI 클라이언트
    keep_recent: 최근 유지할 메시지 수
  """
  if len(messages) <= keep_recent + 2:  # system + 최근 메시지
    return messages

  system_msg = messages[0]
  cut = len(messages) - keep_recent
  # 도구 호출과 결과의 쌍이 경계에서 잘리지 않도록 보정
  while cut < len(messages) and messages[cut].get("role") == "tool":
    cut += 1
  old_messages = messages[1:cut]
  recent_messages = messages[cut:]

  # 오래된 대화 요약 요청
  summary_prompt = (
    "다음은 텍스트 어드벤처 게임의 이전 진행 내용입니다. "
    "핵심 사건과 발견한 것들을 간결하게 요약해주세요.\n\n"
  )
  for msg in old_messages:
    if msg["role"] == "user":
      summary_prompt += f"플레이어: {msg['content']}\n"
    elif msg["role"] == "assistant" and isinstance(msg.get("content"), str):
      summary_prompt += f"게임: {msg['content'][:200]}\n"

  summary_response = client.chat.completions.create(
    model="gpt-5.6-luna",
    messages=[{"role": "user", "content": summary_prompt}],
    reasoning_effort="none",
    temperature=0.3
  )
  summary = summary_response.choices[0].message.content

  # 요약본으로 교체
  summary_msg = {
    "role": "user",
    "content": f"[이전 게임 진행 요약]\n{summary}"
  }

  return [system_msg, summary_msg] + recent_messages


def play_game():
  """게임을 시작하고 실행합니다."""
  state = copy.deepcopy(initial_state)
  messages = [{"role": "system", "content": SYSTEM_PROMPT}]

  # 게임 시작 메시지
  start_msg = (
    f"게임을 시작합니다. 현재 상태: {json.dumps(state, ensure_ascii=False)}\n"
    f"첫 번째 장면을 묘사해주세요."
  )
  messages.append({"role": "user", "content": start_msg})

  # 첫 장면 생성
  response = client.chat.completions.create(
    model="gpt-5.6-luna",
    messages=messages,
    tools=tools,
    reasoning_effort="none",
    temperature=0.9
  )
  message = response.choices[0].message
  messages.append(message.model_dump())  # SDK 객체를 딕셔너리로 변환

  # 도구 호출 처리 (반복 상한으로 무한 호출 방지)
  tool_rounds = 0
  while message.tool_calls and tool_rounds < 5:
    tool_rounds += 1
    tool_results = handle_tool_calls(message)
    messages.extend(tool_results)
    response = client.chat.completions.create(
      model="gpt-5.6-luna",
      messages=messages,
      tools=tools,
      reasoning_effort="none",
      temperature=0.9
    )
    message = response.choices[0].message
    messages.append(message.model_dump())

  # 첫 장면 표시 (배경 묘사일 뿐 행동이 아니므로 상태는 갱신하지 않음)
  try:
    data = parse_response(message.content)
    print(data["narrative"])
  except (json.JSONDecodeError, KeyError, AttributeError):
    print(message.content or "(장면을 생성하지 못했습니다)")
  display_status(state)

  # 메인 게임 루프
  while not state["game_over"] and not state["game_clear"]:
    user_input = input("> ")
    if user_input.lower() in ["quit", "종료"]:
      print("게임을 종료합니다.")
      break
    # [예제 보충] 책: '메인 루프에서 사용자 입력을 받은 직후' — 종료 확인 바로 다음에 넣었습니다.
    # 메인 게임 루프 안에서
    if len(messages) > 20:
      messages = summarize_history(messages, client)

    # 현재 상태를 함께 전달
    user_msg = (
      f"[현재 상태: {json.dumps(state, ensure_ascii=False)}]\n"
      f"플레이어 행동: {user_input}"
    )
    messages.append({"role": "user", "content": user_msg})

    # LLM 응답
    response = client.chat.completions.create(
      model="gpt-5.6-luna",
      messages=messages,
      tools=tools,
      reasoning_effort="none",
      temperature=0.9
    )
    message = response.choices[0].message
    messages.append(message.model_dump())

    # 도구 호출 처리 (반복 상한으로 무한 호출 방지)
    tool_rounds = 0
    while message.tool_calls and tool_rounds < 5:
      tool_rounds += 1
      tool_results = handle_tool_calls(message)
      messages.extend(tool_results)
      response = client.chat.completions.create(
        model="gpt-5.6-luna",
        messages=messages,
        tools=tools,
        reasoning_effort="none",
        temperature=0.9
      )
      message = response.choices[0].message
      messages.append(message.model_dump())

    # 응답 처리 (파싱에 실패한 턴은 상태를 바꾸지 않고 무효 처리)
    try:
      data = parse_response(message.content)
      state = apply_state_changes(state, data)
      print(data["narrative"])
    except (json.JSONDecodeError, KeyError, AttributeError):
      print(message.content
            or "(응답을 생성하지 못했습니다. 다른 행동을 입력해보세요.)")
    display_status(state)

  # 게임 종료
  if state["game_over"]:
    print("체력이 0이 되었습니다. 게임 오버.")
  elif state["game_clear"]:
    print(f"{state['day']}일 만에 구조되었습니다!")


# [예제 보충] import할 때 게임이 바로 시작되지 않도록 play_game() 호출을 main 아래로 옮겼습니다.
if __name__ == "__main__":
  play_game()
