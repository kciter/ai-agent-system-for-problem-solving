"""13장의 코어(8장 call_llm 포함)를 14장 실습용으로 옮겨 온 파일입니다.

8장: 재시도(call_with_retry), 타임아웃 클라이언트, 로깅 래퍼(call_llm)
13장: 도구 레지스트리(TOOLS, tool), 훅(HOOKS, hook, run_hooks), 코어 루프(run_agent), load_plugins
"""

import time
import random
import openai
from openai import OpenAI

from dotenv import load_dotenv  # [예제 보충] 3장처럼 .env에서 API 키를 읽음
load_dotenv()  # [예제 보충]

# 8장 '타임아웃과 폴백': 이후 예제들이 쓰는 최종 클라이언트
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


# ---------------------------------------------------------------------------
# 13장 코어: 도구 레지스트리, 훅, 코어 루프, 플러그인 로더
# ---------------------------------------------------------------------------

TOOLS = {}

def tool(description, parameters):
  """함수를 도구로 등록하는 데코레이터입니다."""
  def decorator(func):
    TOOLS[func.__name__] = {
      "func": func,
      "schema": {
        "type": "function",
        "function": {
          "name": func.__name__,
          "description": description,
          "parameters": parameters
        }
      }
    }
    return func
  return decorator


HOOKS = {}

def hook(event):
  """함수를 특정 이벤트의 훅으로 등록하는 데코레이터입니다."""
  def decorator(func):
    HOOKS.setdefault(event, []).append(func)
    return func
  return decorator

def run_hooks(event, data):
  """이벤트에 등록된 훅들을 순서대로 실행합니다.

  각 훅은 data 딕셔너리를 받아 수정해서 반환할 수 있습니다.
  """
  for func in HOOKS.get(event, []):
    try:
      data = func(data)
    except Exception as e:
      print(f"[훅 오류] {event}/{func.__name__}: {e}")
  return data


def run_agent(user_message, system_prompt, max_iterations=10,
              temperature=0.2):
  """플러그인 구조로 동작하는 에이전트 코어 루프입니다."""
  data = run_hooks("agent_start", {"message": user_message})
  messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": data["message"]}
  ]

  for _ in range(max_iterations):
    data = run_hooks("before_llm", {"messages": messages})
    messages = data["messages"]

    response = call_llm(
      model="gpt-5.6-luna",
      messages=messages,
      tools=[t["schema"] for t in TOOLS.values()],
      reasoning_effort="none",
      temperature=temperature
    )
    message = response.choices[0].message
    messages.append(message.model_dump())  # SDK 객체를 딕셔너리로 변환

    # 도구 호출이 없으면 작업 완료
    if not message.tool_calls:
      data = run_hooks("agent_end",
                       {"messages": messages, "content": message.content})
      return data["content"]

    for tool_call in message.tool_calls:
      data = {
        "name": tool_call.function.name,
        "args": json.loads(tool_call.function.arguments),
        "blocked": False,
        "result": None
      }
      data = run_hooks("before_tool", data)

      if not data["blocked"]:
        entry = TOOLS.get(data["name"])
        if entry is None:
          data["result"] = "알 수 없는 도구입니다."
        else:
          try:
            data["result"] = entry["func"](**data["args"])
          except Exception as e:
            data["result"] = f"도구 호출 중 오류가 발생했습니다: {e}"

      data = run_hooks("after_tool", data)
      messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": str(data["result"])
      })

  return "반복 상한에 도달했습니다."


import importlib
import pathlib

def load_plugins(directory="plugins"):
  """디렉터리 안의 파이썬 파일들을 플러그인으로 불러옵니다."""
  for path in sorted(pathlib.Path(directory).glob("*.py")):
    importlib.import_module(f"{directory}.{path.stem}")
