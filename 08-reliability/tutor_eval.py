"""8장: 6장 영어 튜터에 형식 보장(Structured Outputs)과 평가 세트를 적용합니다.

- SYSTEM_PROMPT는 6장 '구현: 튜터 에이전트'의 것을 그대로 가져왔습니다.
- TUTOR_RESPONSE_FORMAT과 평가 세트(eval_cases, run_eval)는 8장 코드입니다.
- 책에서 `messages`가 이미 있다고 보고 바로 요청을 보내는 Structured Outputs 요청은 함수로 감쌌고,
  마지막 `run_eval()` 호출은 `if __name__ == "__main__":` 아래로 옮겼습니다.

실행: python tutor_eval.py  (평가 세트 6문장을 돌리고 통과 수를 출력합니다)
"""

import json

from reliability import client  # [예제 보충] 8장의 클라이언트(timeout=30.0, max_retries=0)


# 6장 튜터의 시스템 프롬프트 (6장에서 복사)
SYSTEM_PROMPT = """당신은 친절한 영어 회화 튜터입니다. 학습자와 영어로
일상 대화를 나누며 회화 연습을 돕습니다.

## 대화 규칙
- 항상 영어로 대화합니다. 자연스러운 구어체를 사용하세요.
- 학습자가 대답하기 쉽도록, 응답 끝에 가벼운 질문을 덧붙이세요.
- 학습자의 수준에 맞추세요. 학습자가 짧고 단순한 문장을 쓰면
  당신도 쉬운 어휘로 대답하고, 유창하면 자연스러운 속도로 대화하세요.
- 응답은 두세 문장 이내로 짧게 유지하세요. 대화의 주인공은 학습자입니다.

## 교정 규칙
- 학습자의 문장에 명백한 문법 오류나 부자연스러운 표현이 있으면 교정하세요.
- 교정 이유는 한국어로 짧게 설명하세요.
- 사소한 문제이거나 확신이 없으면 교정하지 마세요. 틀린 교정은
  교정하지 않는 것보다 해롭습니다.
- 음성 인식 과정에서 생긴 것으로 보이는 오류(문맥에 맞지 않는 단어 등)는
  교정 대상이 아닙니다.

## 응답 형식
반드시 다음 JSON 형식으로 응답하세요.

{"reply": "학습자에게 들려줄 영어 응답",
 "correction": "교정 내용과 이유 (한국어, 교정할 것이 없으면 null)",
 "better_expression": "더 자연스러운 표현 제안 (없으면 null)"}
"""


# ---------------------------------------------------------------------------
# 8장 '형식 검증: 응답의 모양을 보장하기'
# ---------------------------------------------------------------------------

TUTOR_RESPONSE_FORMAT = {
  "type": "json_schema",
  "json_schema": {
    "name": "tutor_response",
    "strict": True,
    "schema": {
      "type": "object",
      "properties": {
        "reply": {
          "type": "string",
          "description": "학습자에게 들려줄 영어 응답"
        },
        "correction": {
          "type": ["string", "null"],
          "description": "교정 내용과 이유. 없으면 null"
        },
        "better_expression": {
          "type": ["string", "null"],
          "description": "더 자연스러운 표현 제안. 없으면 null"
        }
      },
      "required": ["reply", "correction", "better_expression"],
      "additionalProperties": False
    }
  }
}


# [예제 보충] 책은 6장 대화의 messages가 있다고 보고 아래 요청을 바로 보냅니다. 함수로 감쌌습니다.
def get_structured_tutor_response(messages):
  """TUTOR_RESPONSE_FORMAT으로 튜터 응답을 요청합니다."""
  response = client.chat.completions.create(
    model="gpt-5.6-luna",
    messages=messages,
    response_format=TUTOR_RESPONSE_FORMAT
  )
  data = json.loads(response.choices[0].message.content)
  # reply, correction, better_expression의 존재가 보장됨
  return data  # [예제 보충]


eval_cases = [
  # (학습자 발화, 교정이 필요한가)
  ("I went to the park yesterday.", False),
  ("He go to school every day.", True),
  ("I am agree with you.", True),
  ("She has lived here for three years.", False),
  ("I look forward to seeing you.", False),
  ("Yesterday I eat pizza with my friend.", True),
]

def run_eval():
  """평가 세트로 튜터의 교정 판단을 검사합니다."""
  passed = 0
  for sentence, needs_correction in eval_cases:
    messages = [
      {"role": "system", "content": SYSTEM_PROMPT},
      {"role": "user", "content": sentence}
    ]
    response = client.chat.completions.create(
      model="gpt-5.6-luna",
      messages=messages,
      response_format=TUTOR_RESPONSE_FORMAT,
      reasoning_effort="none",
      temperature=0
    )
    data = json.loads(response.choices[0].message.content)
    corrected = data["correction"] is not None

    if corrected == needs_correction:
      passed += 1
    else:
      print(f"불일치: '{sentence}' "
            f"(기대: {needs_correction}, 실제: {corrected})")

  print(f"결과: {passed}/{len(eval_cases)} 통과")


if __name__ == "__main__":
  run_eval()
