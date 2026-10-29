"""6장 영어 회화 연습 에이전트.

책 6장의 코드를 나온 순서대로 이어 붙였습니다(녹음과 재생 → 음성 인식 → 시스템 프롬프트 →
튜터 응답 → 음성 합성 → 메인 루프 → 세션 보고서). 책과 다른 점은 마지막 실행 줄
`practice_session()`을 `if __name__ == "__main__":` 아래로 옮긴 것 하나입니다
(다른 파일에서 import할 때 세션이 바로 시작되지 않도록).

실행: python english_tutor.py  (.env에 OPENAI_API_KEY, 마이크와 스피커 필요)
"""

import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16000  # 음성 인식용으로 충분한 샘플레이트

def record_audio(filename, seconds=5):
  """마이크로 음성을 녹음하여 파일로 저장합니다."""
  print("말씀하세요...")
  audio = sd.rec(
    int(seconds * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16"
  )
  sd.wait()  # 녹음이 끝날 때까지 대기
  sf.write(filename, audio, SAMPLE_RATE)
  print("녹음 완료")

def play_audio(filename):
  """오디오 파일을 스피커로 재생합니다."""
  data, samplerate = sf.read(filename, dtype="int16")
  sd.play(data, samplerate)
  sd.wait()  # 재생이 끝날 때까지 대기


import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def transcribe(filename):
  """음성 파일을 텍스트로 변환합니다."""
  with open(filename, "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
      model="gpt-4o-mini-transcribe",
      file=audio_file,
      language="en"
    )
  return transcription.text


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


import json

def get_tutor_response(messages):
  """튜터의 응답을 생성하고 JSON으로 파싱합니다."""
  response = client.chat.completions.create(
    model="gpt-5.6-luna",
    messages=messages,
    response_format={"type": "json_object"},
    reasoning_effort="none",
    temperature=0.7
  )
  content = response.choices[0].message.content
  messages.append({"role": "assistant", "content": content})
  data = json.loads(content)
  if "reply" not in data:  # 필수 키가 빠진 응답에 대한 방어
    data["reply"] = "Sorry, could you say that again?"
  return data


def speak(text, filename="reply.wav"):
  """텍스트를 음성으로 변환하여 재생합니다."""
  with client.audio.speech.with_streaming_response.create(
    model="gpt-4o-mini-tts",
    voice="coral",
    input=text,
    instructions="Speak clearly and at a moderate pace, "
                 "like a friendly English tutor.",
    response_format="wav"
  ) as response:
    response.stream_to_file(filename)
  play_audio(filename)


def practice_session():
  """영어 회화 연습 세션을 시작합니다."""
  messages = [{"role": "system", "content": SYSTEM_PROMPT}]

  print("영어 회화 연습을 시작합니다.")
  print("Enter를 누르면 5초간 녹음됩니다. 종료하려면 q를 입력하세요.\n")

  # 튜터가 먼저 인사하며 대화를 시작
  messages.append({
    "role": "user",
    "content": "(세션이 시작되었습니다. 학습자에게 영어로 인사하고 "
               "가벼운 주제로 대화를 시작해주세요.)"
  })
  data = get_tutor_response(messages)
  print(f"튜터: {data['reply']}\n")
  speak(data["reply"])

  while True:
    command = input("[Enter: 말하기 / q: 종료] ")
    if command.strip().lower() == "q":
      break

    # 1단계: 녹음
    record_audio("input.wav")

    # 2단계: 음성 인식 (STT)
    user_text = transcribe("input.wav")
    print(f"나: {user_text}")

    # 3단계: 튜터 응답 생성 (LLM)
    messages.append({"role": "user", "content": user_text})
    data = get_tutor_response(messages)

    if data.get("correction"):
      print(f"  [교정] {data['correction']}")
    if data.get("better_expression"):
      print(f"  [제안] {data['better_expression']}")
    print(f"튜터: {data['reply']}\n")

    # 4단계: 음성 합성 및 재생 (TTS)
    speak(data["reply"])

  # 세션 종료 후 학습 보고서 생성
  generate_report(messages)


def generate_report(messages):
  """세션 전체 대화를 바탕으로 학습 보고서를 생성합니다."""
  # 시스템 프롬프트와 세션 시작 지시문을 제외한 대화 히스토리를 정리
  conversation = ""
  for msg in messages[2:]:
    if msg["role"] == "user":
      conversation += f"학습자: {msg['content']}\n"
    elif msg["role"] == "assistant":
      conversation += f"튜터: {msg['content']}\n"

  report_prompt = (
    "다음은 영어 회화 연습 세션의 기록입니다. 학습자를 위한 보고서를 "
    "한국어로 작성해주세요. 다음 내용을 포함하세요.\n"
    "1. 반복적으로 나타난 실수 패턴\n"
    "2. 잘 사용한 표현\n"
    "3. 다음 연습에서 시도해볼 표현이나 주제\n"
    "터미널에 그대로 출력되므로 마크다운 서식 없이 "
    "일반 텍스트로 작성하세요.\n\n"
    f"{conversation}"
  )

  response = client.chat.completions.create(
    model="gpt-5.6-luna",
    messages=[{"role": "user", "content": report_prompt}],
    reasoning_effort="none",
    temperature=0.3
  )

  print("\n===== 오늘의 학습 보고서 =====")
  print(response.choices[0].message.content)


if __name__ == "__main__":
  practice_session()
