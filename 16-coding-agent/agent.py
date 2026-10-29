"""16장 코딩 에이전트의 코어(agent.py).

13장의 구조(agent.py는 코어, 실행은 main.py, 도구와 훅은 plugins/)를 그대로 따릅니다.
- 8장: 재시도(call_with_retry)와 로깅 래퍼(call_llm)
- 13장: 도구 레지스트리(TOOLS, tool), 훅(HOOKS, hook, run_hooks), 플러그인 로더(load_plugins)
- 16장: 시스템 프롬프트, run_turn, coding_agent

책 블록 끝의 `coding_agent()` 호출은 main.py로 옮겼습니다. 이 파일에 두고
`python agent.py`로 실행하면 13장 :351에서 설명한 이중 import 문제가 생깁니다.
"""

from dotenv import load_dotenv  # [예제 보충] 3장처럼 .env에서 OPENAI_API_KEY를 읽습니다
load_dotenv()  # [예제 보충]

# ---- 8장: 재시도 ----

import time
import random
import openai
from openai import OpenAI

client = OpenAI(timeout=30.0, max_retries=0)  # 8장 '타임아웃과 폴백' 절의 최종 설정

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

# ---- 8장: 로깅 래퍼 ----

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

# ---- 13장: 도구 레지스트리 ----

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

# ---- 13장: 훅 ----

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

# ---- 13장: 플러그인 로더 ----

import importlib
import pathlib

def load_plugins(directory="plugins"):
  """디렉터리 안의 파이썬 파일들을 플러그인으로 불러옵니다."""
  for path in sorted(pathlib.Path(directory).glob("*.py")):
    importlib.import_module(f"{directory}.{path.stem}")

# ---- 16장: 시스템 프롬프트 ----

CODING_SYSTEM_PROMPT = """당신은 코딩 에이전트입니다. 사용자의 요청에 따라
작업 디렉터리의 코드를 읽고, 수정하고, 실행해 확인합니다.

## 작업 방식
1. 어느 파일을 봐야 할지 모르면 search_code와 list_files로 찾고,
   read_file로 내용을 확인하세요. 추측하지 말고 실제 코드를 읽으세요.
2. 수정은 edit_file로 필요한 부분만 바꾸세요. 새 파일을 만들 때만
   write_file을 사용하세요.
3. 수정 후에는 run_command로 실행하거나 테스트하여 결과를 확인하세요.
   "고쳤습니다."로 끝내지 말고, 실제로 동작하는지 검증하세요.
4. 실행이 실패하면 오류 메시지를 읽고 다시 수정하세요.

## 원칙
- 요청받지 않은 파일은 수정하지 마세요.
- 파괴적인 명령(파일 삭제 등)은 꼭 필요할 때만 사용하세요.
- 작업이 끝나면 무엇을 왜 했는지 간단히 설명하세요.
"""

# ---- 16장: 멀티턴 루프 ----

def run_turn(messages, max_iterations=15, temperature=0.2):
  """대화 히스토리 위에서 한 턴을 실행하고, 응답과 갱신된 히스토리를
  함께 반환합니다 (13장 run_agent의 멀티턴판)."""
  for _ in range(max_iterations):
    data = run_hooks("before_llm", {"messages": messages})
    messages = data["messages"]  # 요약 훅 등이 리스트를 교체할 수 있음

    response = call_llm(
      model="gpt-5.6-luna",
      messages=messages,
      tools=[t["schema"] for t in TOOLS.values()],
      reasoning_effort="none",
      temperature=temperature
    )
    message = response.choices[0].message
    if message.content and message.tool_calls: # 호출 전 설명이 있으면 보여줌
      print(message.content)
    messages.append(message.model_dump())

    if not message.tool_calls:
      data = run_hooks("agent_end",
                       {"messages": messages, "content": message.content})
      return data["content"], messages

    for tool_call in message.tool_calls:
      print(f"[도구 호출] {tool_call.function.name}: "
            f"{tool_call.function.arguments}")
      data = {
        "name": tool_call.function.name,
        "args": json.loads(tool_call.function.arguments),
        "blocked": False,
        "result": None
      }
      data = run_hooks("before_tool", data)  # 승인 게이트

      if not data["blocked"]:
        entry = TOOLS.get(data["name"])
        if entry is None:
          data["result"] = "알 수 없는 도구입니다."
        else:
          try:
            data["result"] = entry["func"](**data["args"])
          except Exception as e:
            data["result"] = f"도구 호출 중 오류가 발생했습니다: {e}"

      data = run_hooks("after_tool", data)  # 감사 로그
      messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": str(data["result"])
      })

  # 반복 상한: 히스토리에도 남겨 다음 턴이 맥락을 잃지 않게 함
  limit_msg = "반복 상한에 도달했습니다. 작업을 나눠서 다시 요청해주세요."
  messages.append({"role": "assistant", "content": limit_msg})
  return limit_msg, messages

def coding_agent():
  """코딩 에이전트와의 대화 세션입니다."""
  load_plugins()  # 도구와 훅이 등록된 플러그인 로딩 (13장)
  messages = [{"role": "system", "content": CODING_SYSTEM_PROMPT}]

  print("코딩 에이전트입니다. 무엇을 도와드릴까요? (종료: q)")
  while True:
    user_input = input("\n> ")
    if user_input.strip().lower() == "q":
      break
    messages.append({"role": "user", "content": user_input})
    answer, messages = run_turn(messages)  # 갱신된 히스토리를 이어받음
    print(answer)
