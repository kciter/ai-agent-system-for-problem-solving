"""8장 신뢰성 계층: 재시도, 폴백, 형식 재요청, 로깅. (08-reliability/reliability.py와 같은 파일)

책 8장의 코드 조각을 나온 순서대로 모았습니다.
- 클라이언트는 책에 나온 순서대로 두 번 만듭니다. '재시도 전략'의 `OpenAI(max_retries=0)` 다음에
  '타임아웃과 폴백' 절의 최종 설정 `OpenAI(timeout=30.0, max_retries=0)`으로 바꿉니다.
  그 사이에 나오는 한 줄짜리 설정 예시(`max_retries=3`, `timeout=30.0`)는 설명용이라 넣지 않았습니다.
- '재시도 전략'의 사용 예는 `if __name__ == "__main__":` 아래로 옮겼습니다.

실행: python reliability.py  (.env에 OPENAI_API_KEY 필요)
"""

import time
import random
import openai
from openai import OpenAI
from dotenv import load_dotenv  # [예제 보충] 3장처럼 .env에서 API 키를 읽습니다.

load_dotenv()  # [예제 보충]
client = OpenAI(max_retries=0)  # 재시도는 call_with_retry가 전담
# '타임아웃과 폴백' 절의 최종 클라이언트("이후 예제들은 모두 이 클라이언트를 사용한다고 가정합니다").
client = OpenAI(timeout=30.0, max_retries=0)

# 재시도할 가치가 있는 예외들
RETRYABLE_ERRORS = (
  openai.APIConnectionError,   # 네트워크 문제 (타임아웃 포함)
  openai.RateLimitError,       # 레이트 리밋 (429)
  openai.InternalServerError,  # 서버 오류 (500번대)
)

def call_with_retry(request_fn, max_retries=3):
  """실패 시 지수 백오프로 재시도하며 요청을 실행합니다.

  Args:
    request_fn: 실제 API 요청을 실행하는 함수
    max_retries: 최대 재시도 횟수
  """
  for attempt in range(max_retries + 1):
    try:
      return request_fn()
    except RETRYABLE_ERRORS as e:
      if attempt == max_retries:
        raise  # 재시도를 다 써도 실패하면 예외를 올림
      delay = 2 ** attempt + random.uniform(0, 1)  # 백오프 + 지터
      print(f"호출 실패({type(e).__name__}). "
            f"{delay:.1f}초 후 재시도합니다.")
      time.sleep(delay)


def chat_with_fallback(messages, **kwargs):
  """주 모델이 실패하면 예비 모델로 폴백합니다."""
  try:
    return call_with_retry(
      lambda: client.chat.completions.create(
        model="gpt-5.6-luna", messages=messages, **kwargs
      )
    )
  except RETRYABLE_ERRORS:
    print("주 모델 호출에 실패했습니다. 예비 모델로 전환합니다.")
    return client.chat.completions.create(
      model="gpt-5.6-terra", messages=messages, **kwargs
    )


def get_json_response(messages, required_keys, max_attempts=3):
  """JSON 응답을 요청하고, 형식이 어긋나면 재요청합니다."""
  attempt_messages = list(messages)

  for _ in range(max_attempts):
    response = client.chat.completions.create(
      model="gpt-5.6-luna",
      messages=attempt_messages,
      response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content

    try:
      data = json.loads(content)
    except json.JSONDecodeError:
      error_note = "응답이 유효한 JSON이 아닙니다. 다시 생성해주세요."
    else:
      missing = [k for k in required_keys if k not in data]
      if not missing:
        return data  # 검증 통과
      error_note = f"다음 키가 누락되었습니다: {missing}. 다시 생성해주세요."

    # 실패한 응답과 오류 내용을 대화에 추가하고 재요청
    attempt_messages.append({"role": "assistant", "content": content})
    attempt_messages.append({"role": "user", "content": error_note})

  raise ValueError("유효한 형식의 응답을 얻지 못했습니다.")


import time
import json
from datetime import datetime

def call_llm(trace_id=None, **kwargs):
  """재시도와 로깅을 더한 LLM 호출 래퍼입니다."""
  log = {
    "timestamp": datetime.now().isoformat(),
    "trace_id": trace_id,
    "model": kwargs.get("model"),
  }
  start = time.time()

  try:
    response = call_with_retry(
      lambda: client.chat.completions.create(**kwargs)
    )
  except Exception as e:
    log["status"] = "error"
    log["error"] = f"{type(e).__name__}: {e}"
    log["latency"] = round(time.time() - start, 2)
    write_log(log)
    raise

  log["status"] = "success"
  log["latency"] = round(time.time() - start, 2)
  log["prompt_tokens"] = response.usage.prompt_tokens
  log["completion_tokens"] = response.usage.completion_tokens
  write_log(log)
  return response

def write_log(log):
  """로그를 JSON Lines 형식으로 파일에 기록합니다."""
  with open("llm_calls.jsonl", "a") as f:
    f.write(json.dumps(log, ensure_ascii=False) + "\n")


if __name__ == "__main__":
  # 사용 예
  response = call_with_retry(
    lambda: client.chat.completions.create(
      model="gpt-5.6-luna",
      messages=[{"role": "user", "content": "안녕하세요."}]
    )
  )
  print(response.choices[0].message.content)  # [예제 보충] 받은 응답을 화면에 보여줍니다.
