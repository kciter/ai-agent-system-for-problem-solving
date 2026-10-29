"""9장 비용: 단가표와 비용 계산, 로그 집계, 응답 캐싱.

8장의 call_llm이 남긴 llm_calls.jsonl을 읽어 비용을 계산합니다.
책의 `summarize_costs()` 실행 줄은 `if __name__ == "__main__":` 아래로 옮겼습니다.

실행: python cost.py  (현재 디렉터리의 llm_calls.jsonl을 집계합니다)
"""

import json  # [예제 보충] 책에서는 8장 코드의 import json을 함께 씁니다.

from reliability import call_llm  # [예제 보충] 8장 신뢰성 계층


PRICE_PER_1M = {
  # 집필 시점 기준, 100만 토큰당 달러
  "gpt-5.6-luna": {"input": 0.20, "output": 1.20},
  "gpt-5.6-terra": {"input": 2.00, "output": 12.00},
}

def calculate_cost(model, prompt_tokens, completion_tokens):
  """토큰 사용량으로 호출 비용을 계산합니다."""
  price = PRICE_PER_1M[model]
  return (prompt_tokens * price["input"]
          + completion_tokens * price["output"]) / 1_000_000

def summarize_costs(log_file="llm_calls.jsonl"):
  """로그 파일에서 총비용과 호출 수를 집계합니다."""
  total_cost = 0
  call_count = 0
  with open(log_file) as f:
    for line in f:
      log = json.loads(line)
      if log.get("status") != "success":
        continue
      call_count += 1
      total_cost += calculate_cost(
        log["model"],
        log["prompt_tokens"],
        log["completion_tokens"]
      )
  print(f"호출 수: {call_count}, 총비용: ${total_cost:.4f}")


import hashlib

_response_cache = {}

def cached_llm_call(**kwargs):
  """같은 요청이 반복되면 저장된 응답을 재사용합니다."""
  key = hashlib.sha256(
    json.dumps(kwargs, sort_keys=True, ensure_ascii=False).encode()
  ).hexdigest()

  if key in _response_cache:
    return _response_cache[key]

  response = call_llm(**kwargs)
  _response_cache[key] = response
  return response


if __name__ == "__main__":
  summarize_costs()
