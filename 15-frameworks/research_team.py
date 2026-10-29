"""15장 그래프 노드가 부르는 앞 장의 함수들(7장, 8장, 12장에서 가져옴).

12장 리서치 팀의 plan_subtopics, run_workers, write_report, evaluate_report와
그 함수들이 쓰는 코드를 책에서 그대로 옮겼습니다. 12장 본문(244쪽)의 전제대로
run_research, write_report, evaluate_report의 LLM 호출은 8장 마지막에서 한 것처럼
call_llm으로 바꾼 버전입니다(바꾼 줄에 '8장:' 주석).
"""

# ---- 7장: 기본 설정 ----

import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

import uuid  # [예제 보충] trace_id 생성용(8장 192쪽)

# ---- 8장: 재시도, 타임아웃 ----

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

# ---- 7장: 도구 ----

import time
from ddgs import DDGS

def search_web(query, max_results=5):
  """웹에서 검색하고 결과 목록을 문자열로 반환합니다."""
  try:
    results = DDGS().text(query, max_results=max_results)
  except Exception as e:
    return f"검색 중 오류가 발생했습니다: {e}"

  if not results:
    return "검색 결과가 없습니다. 다른 검색어를 시도해보세요."

  lines = []
  for r in results:
    lines.append(
      f"- 제목: {r['title']}\n"
      f"  주소: {r['href']}\n"
      f"  요약: {r['body']}"
    )
  time.sleep(1)  # 연속 검색 시 차단을 피하기 위한 지연
  return "\n".join(lines)

import trafilatura

def read_webpage(url):
  """웹 페이지의 본문을 추출하여 반환합니다."""
  html = trafilatura.fetch_url(url)
  if html is None:
    return "페이지를 가져올 수 없습니다. 다른 페이지를 시도해보세요."

  text = trafilatura.extract(html)
  if text is None:
    return "본문을 추출할 수 없습니다. 다른 페이지를 시도해보세요."

  return text[:4000]  # 지나치게 긴 본문은 잘라서 반환

tools = [
  {
    "type": "function",
    "function": {
      "name": "search_web",
      "description": "웹에서 검색합니다. 제목, 주소, 요약으로 이루어진 "
                     "검색 결과 목록을 반환합니다. 자세한 내용이 필요하면 "
                     "결과의 주소를 read_webpage로 읽어야 합니다.",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "검색어. 구체적일수록 좋습니다."
          },
          "max_results": {
            "type": "integer",
            "description": "가져올 검색 결과 수 (기본 5)"
          }
        },
        "required": ["query"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "read_webpage",
      "description": "웹 페이지의 본문을 읽습니다. 검색 결과의 요약만으로 "
                     "부족할 때, 출처로 인용할 내용을 확인할 때 사용합니다.",
      "parameters": {
        "type": "object",
        "properties": {
          "url": {
            "type": "string",
            "description": "읽을 페이지의 주소"
          }
        },
        "required": ["url"]
      }
    }
  }
]

# ---- 7장: 조사 루프 (8장의 call_llm 적용) ----

RESEARCH_SYSTEM_PROMPT = """당신은 주어진 주제를 조사하는 리서치 에이전트입니다.

## 작업 방식
1. 주제를 파악하고 무엇을 검색할지 계획하세요.
2. search_web으로 검색하고, 중요해 보이는 페이지는 read_webpage로
   직접 읽으세요. 검색 결과의 짧은 요약만 보고 판단하지 마세요.
3. 하나의 출처에 의존하지 말고, 서로 다른 출처를 3개 이상 확인하세요.
4. 정보가 충분히 모였다고 판단되면 도구 호출을 멈추고,
   수집한 정보를 정리해서 응답하세요.

## 조사 노트 규칙
- 수집한 정보를 정리할 때는 각 정보를 어느 페이지(URL)에서
  얻었는지 반드시 함께 기록하세요.
- 페이지에서 확인한 내용만 기록하세요. 추측이나 사전 지식으로
  내용을 보충하지 마세요.
"""

def run_research(topic, max_iterations=10):
  """주제를 조사하고 출처가 달린 조사 노트를 반환합니다."""
  trace_id = str(uuid.uuid4())  # [예제 보충] 8장 본문(192쪽)대로 요청마다 식별자를 만듭니다
  messages = [
    {"role": "system", "content": RESEARCH_SYSTEM_PROMPT},
    {"role": "user", "content": f"다음 주제를 조사해주세요: {topic}"}
  ]

  for _ in range(max_iterations):
    response = call_llm(  # 8장: 신뢰성 계층을 적용한 코드
      trace_id=trace_id,
      model="gpt-5.6-luna",
      messages=messages,
      tools=tools,
      reasoning_effort="none",
      temperature=0.2
    )
    message = response.choices[0].message
    messages.append(message)

    # 도구 호출이 없으면 조사 완료
    if not message.tool_calls:
      return message.content

    # 도구 호출 처리
    for tool_call in message.tool_calls:
      args = json.loads(tool_call.function.arguments)
      name = tool_call.function.name
      print(f"[도구 호출] {name}: {args}")

      try:
        if name == "search_web":
          result = search_web(**args)
        elif name == "read_webpage":
          result = read_webpage(**args)
        else:
          result = "알 수 없는 도구입니다."
      except Exception as e:
        result = f"도구 호출 중 오류가 발생했습니다: {e}"

      messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result
      })

  # 반복 상한 도달: 지금까지 모은 정보로 마무리
  messages.append({
    "role": "user",
    "content": "조사를 마무리하고 지금까지 수집한 정보를 정리해주세요."
  })
  response = call_llm(  # 8장: call_llm으로 교체
    trace_id=trace_id,
    model="gpt-5.6-luna",
    messages=messages,
    reasoning_effort="none",
    temperature=0.2
  )
  return response.choices[0].message.content

# ---- 7장: 보고서 작성 (8장의 call_llm 적용) ----

def write_report(topic, research_notes):
  """조사 노트를 바탕으로 보고서를 작성합니다."""
  trace_id = str(uuid.uuid4())  # [예제 보충] 8장 본문(192쪽): "시작될 때 uuid.uuid4() 같은 방법으로 하나 만들어" (문자열로 바꿔야 write_log가 기록할 수 있음)
  prompt = (
    f"다음은 '{topic}'에 대한 조사 노트입니다. "
    "이를 바탕으로 마크다운 형식의 보고서를 작성해주세요.\n\n"
    "## 작성 규칙\n"
    "- 개요, 주요 내용, 시사점, 참고 자료 순으로 구성하세요.\n"
    "- 조사 노트에 있는 내용만 사용하세요. 노트에 없는 사실을 "
    "추가하지 마세요.\n"
    "- 주요 내용의 각 항목에는 근거가 된 출처(URL)를 표기하세요.\n"
    "- 참고 자료 절에 사용한 모든 출처를 나열하세요.\n\n"
    f"## 조사 노트\n{research_notes}"
  )
  response = call_llm(  # 8장: call_llm으로 교체
    trace_id=trace_id,
    model="gpt-5.6-luna",
    messages=[{"role": "user", "content": prompt}],
    reasoning_effort="none",
    temperature=0.3
  )
  return response.choices[0].message.content

# ---- 8장: LLM 평가자 (call_llm 적용) ----

EVALUATOR_FORMAT = {
  "type": "json_schema",
  "json_schema": {
    "name": "evaluation",
    "strict": True,
    "schema": {
      "type": "object",
      "properties": {
        "passed": {"type": "boolean"},
        "problems": {
          "type": "array",
          "items": {"type": "string"}
        }
      },
      "required": ["passed", "problems"],
      "additionalProperties": False
    }
  }
}

def evaluate_report(research_notes, report):
  """보고서가 조사 노트에 근거하는지 평가합니다."""
  trace_id = str(uuid.uuid4())  # [예제 보충] 8장 본문(192쪽): "시작될 때 uuid.uuid4() 같은 방법으로 하나 만들어" (문자열로 바꿔야 write_log가 기록할 수 있음)
  prompt = (
    "다음 보고서를 검증해주세요.\n\n"
    "## 검증 기준\n"
    "- 보고서의 모든 주장이 조사 노트에 근거하는가?\n"
    "- 조사 노트에 없는 사실이 추가되지 않았는가?\n"
    "- 출처 표기가 조사 노트의 출처와 일치하는가?\n\n"
    "기준을 모두 만족하면 passed를 true로, 하나라도 어긋나면 "
    "false로 판정하고 문제를 problems에 나열하세요.\n\n"
    f"## 조사 노트\n{research_notes}\n\n"
    f"## 보고서\n{report}"
  )
  response = call_llm(  # 8장: call_llm으로 교체
    trace_id=trace_id,
    model="gpt-5.6-luna",
    messages=[{"role": "user", "content": prompt}],
    response_format=EVALUATOR_FORMAT,
    reasoning_effort="none",
    temperature=0
  )
  return json.loads(response.choices[0].message.content)

# ---- 12장: 오케스트레이터와 워커 ----

SUBTOPICS_FORMAT = {
  "type": "json_schema",
  "json_schema": {
    "name": "subtopics",
    "strict": True,
    "schema": {
      "type": "object",
      "properties": {
        "subtopics": {
          "type": "array",
          "items": {"type": "string"}
        }
      },
      "required": ["subtopics"],
      "additionalProperties": False
    }
  }
}

def plan_subtopics(topic, count=3):
  """주제를 독립적으로 조사할 수 있는 하위 질문으로 분해합니다."""
  prompt = (
    f"다음 주제를 조사하려고 합니다: {topic}\n\n"
    f"이 주제를 하위 질문 {count}개로 분해해주세요.\n"
    "- 각 질문은 다른 질문과 겹치지 않고 독립적으로 조사할 수 "
    "있어야 합니다.\n"
    "- 하위 질문들을 합치면 주제 전체를 포괄해야 합니다."
  )
  response = call_llm(
    model="gpt-5.6-luna",
    messages=[{"role": "user", "content": prompt}],
    response_format=SUBTOPICS_FORMAT,
    reasoning_effort="none",
    temperature=0.3
  )
  return json.loads(response.choices[0].message.content)["subtopics"]

from concurrent.futures import ThreadPoolExecutor

def run_workers(subtopics):
  """하위 질문들을 조사 워커들에게 분배하고 병렬로 실행합니다."""
  with ThreadPoolExecutor(max_workers=3) as executor:
    notes = list(executor.map(run_research, subtopics))
  return notes
