"""11장 컨텍스트와 메모리.

책 11장의 코드를 순서대로 이어 붙였습니다(memory_v1.py의 첫 버전은 제외).
  - 압축: COMPACT_THRESHOLD, COMPACT_PROMPT, compact_if_needed
  - 임베딩: embed, cosine_similarity
  - 의미 검색 기억 저장소: load_memory_store, remember, recall
  - RAG: answer_with_docs, split_into_chunks

call_llm과 client는 8장의 신뢰성 계층을 그대로 가져왔습니다(파일 앞부분).
책과 다른 점: 기억을 시험하는 실행 코드(remember 네 번과 print(recall(...)))를
파일 끝의 `if __name__ == "__main__":` 아래로 옮겼습니다.

실행: python memory.py  (.env에 OPENAI_API_KEY 필요, 현재 디렉터리에 memories.json이 생깁니다)
"""

# ---------------------------------------------------------------------------
# 7장 기본 설정과 8장 신뢰성 계층 (8장에서 가져옴)
# ---------------------------------------------------------------------------
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

import time
import random
import openai
from openai import OpenAI

client = OpenAI(timeout=30.0, max_retries=0)  # 8장: 타임아웃 30초, 재시도는 call_with_retry가 전담

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
# 11장: 압축 구현하기
# ---------------------------------------------------------------------------
COMPACT_THRESHOLD = 50_000  # 이 토큰 수를 넘으면 압축

COMPACT_PROMPT = (
  "지금까지의 대화를 다음 구조로 요약해주세요.\n"
  "- 결정: 무엇을 하기로 했는가\n"
  "- 사실: 무엇을 알아냈는가 (출처가 있다면 함께)\n"
  "- 미해결: 남아 있는 질문이나 작업\n"
  "실패한 시도와 중간 과정은 한 줄씩만 남기세요."
)

def compact_if_needed(messages, last_prompt_tokens):
  """컨텍스트가 임곗값을 넘으면 구조화된 요약으로 압축합니다."""
  if last_prompt_tokens < COMPACT_THRESHOLD:
    return messages

  response = call_llm(
    model="gpt-5.6-luna",
    messages=messages + [{"role": "user", "content": COMPACT_PROMPT}],
    reasoning_effort="none",
    temperature=0.3
  )
  summary = response.choices[0].message.content
  return [
    messages[0],  # 시스템 프롬프트는 유지
    {"role": "user", "content": f"[이전 대화 요약]\n{summary}"}
  ]


# ---------------------------------------------------------------------------
# 11장: 의미로 찾기 - 임베딩
# ---------------------------------------------------------------------------
def embed(texts):
  """텍스트 목록을 임베딩 벡터로 변환합니다."""
  response = client.embeddings.create(
    model="text-embedding-3-small",
    input=texts
  )
  return [d.embedding for d in response.data]

def cosine_similarity(a, b):
  """두 벡터가 얼마나 가까운지 계산합니다 (1에 가까울수록 유사)."""
  dot = sum(x * y for x, y in zip(a, b))
  norm_a = sum(x * x for x in a) ** 0.5
  norm_b = sum(y * y for y in b) ** 0.5
  return dot / (norm_a * norm_b)


# 기억 저장소를 의미 검색이 되는 형태로 다시 만듭니다.
import json

MEMORY_FILE = "memories.json"

def load_memory_store():
  """저장된 기억 목록을 읽어옵니다."""
  try:
    with open(MEMORY_FILE, encoding="utf-8") as f:
      return json.load(f)
  except FileNotFoundError:
    return []

def remember(fact):
  """기억을 임베딩과 함께 저장합니다."""
  store = load_memory_store()
  store.append({"text": fact, "vector": embed([fact])[0]})
  with open(MEMORY_FILE, "w", encoding="utf-8") as f:
    json.dump(store, f, ensure_ascii=False)
  return f"기억했습니다: {fact}"

def recall(query, top_k=3):
  """질문과 의미가 가까운 기억을 찾아 반환합니다."""
  store = load_memory_store()
  if not store:
    return "저장된 기억이 없습니다."
  query_vector = embed([query])[0]
  ranked = sorted(
    store,
    key=lambda m: cosine_similarity(query_vector, m["vector"]),
    reverse=True
  )
  return "\n".join(f"- {m['text']}" for m in ranked[:top_k])


# ---------------------------------------------------------------------------
# 11장: 기억에서 지식으로 - RAG
# ---------------------------------------------------------------------------
def answer_with_docs(question, top_k=3):
  """관련 문서 조각을 찾아 컨텍스트로 넣고 답합니다."""
  context = recall(question, top_k=top_k)  # 문서 조각 검색
  prompt = (
    "다음 참고 자료를 근거로 질문에 답해주세요. "
    "자료에 없는 내용은 모른다고 답하세요.\n\n"
    f"## 참고 자료\n{context}\n\n## 질문\n{question}"
  )
  response = call_llm(
    model="gpt-5.6-luna",
    messages=[{"role": "user", "content": prompt}],
    reasoning_effort="none",
    temperature=0.2
  )
  return response.choices[0].message.content


def split_into_chunks(text, chunk_size=800, overlap=100):
  """문서를 겹치는 구간이 있는 조각으로 나눕니다."""
  chunks = []
  start = 0
  while start < len(text):
    chunks.append(text[start:start + chunk_size])
    start += chunk_size - overlap
  return chunks


# 책에서는 recall 바로 뒤에 나오는 시험 코드입니다(import할 때 실행되지 않도록 옮김).
if __name__ == "__main__":
  remember("사용자는 보고서를 표 중심으로 간결하게 받는 것을 선호한다.")
  remember("사용자의 회사는 B2B SaaS를 만드는 30인 규모 스타트업이다.")
  remember("지난 조사에서 경쟁사 A는 4월에 신제품을 출시했다.")
  remember("다음 주 화요일에 팀 워크숍이 예정되어 있다.")

  print(recall("결과물을 어떤 형식으로 만들어야 하지?", top_k=2))
