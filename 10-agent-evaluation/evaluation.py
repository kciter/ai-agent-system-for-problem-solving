"""10장 에이전트 평가: 결과·궤적 평가(인용 검증, 조사 성실성), 루브릭 채점, 평가 하네스, 회귀 비교, 채점자 검증.

리서치 에이전트(7~9장, research_agent.py)를 대상으로 결과와 궤적을 함께 평가합니다.
- run_research_traced는 책의 뼈대에 8장 run_research의 루프 본문을 채워 넣었습니다
  (책: "루프 본문은 7장의 run_research와 같고, 도구를 실행한 지점에 아래 한 줄이 추가됩니다").
- 실행 줄 `run_eval_suite()`는 책에 없어서 `if __name__ == "__main__":` 아래에 보충했습니다.

실행: python evaluation.py  (.env에 OPENAI_API_KEY 필요, 평가 주제 3개로 실제 조사를 돌립니다)
"""

import json  # [예제 보충]
import uuid  # [예제 보충] run_research_traced의 trace_id

from reliability import call_llm  # [예제 보충] 8장
from research_agent import (  # [예제 보충] 7~9장의 리서치 에이전트
  RESEARCH_SYSTEM_PROMPT, tools, search_web, read_webpage, write_report, evaluate_report
)


# ---------------------------------------------------------------------------
# 채점자를 채점하기
# ---------------------------------------------------------------------------

def validate_judge(labeled_cases):
  """사람이 채점한 사례로 LLM 채점자의 일치율을 측정합니다.

  labeled_cases: [{"notes": ..., "report": ..., "human_pass": bool}, ...]
  """
  agree = 0
  for case in labeled_cases:
    verdict = evaluate_report(case["notes"], case["report"])
    if verdict["passed"] == case["human_pass"]:
      agree += 1
    else:
      print(f"불일치: 사람={case['human_pass']}, "
            f"채점자={verdict['passed']}")
  rate = agree / len(labeled_cases)
  print(f"채점자-사람 일치율: {rate:.0%}")
  return rate


# ---------------------------------------------------------------------------
# 구현: 리서치 에이전트의 평가 하네스
# ---------------------------------------------------------------------------

def run_research_traced(topic, max_iterations=10):
  """조사를 실행하며 도구 호출 궤적을 함께 기록합니다."""
  trajectory = []  # (도구 이름, 인자, 결과) 기록

  # 루프 본문은 7장의 run_research와 같고,
  # 도구를 실행한 지점에 아래 한 줄이 추가됩니다
  #   trajectory.append((name, args, result))
  # [예제 보충] 여기부터는 8장에서 call_llm을 적용한 run_research의 본문 그대로이고,
  # 도구를 실행한 지점에 trajectory.append 한 줄, 끝에 노트와 궤적을 함께 반환하는 부분만 다릅니다.
  trace_id = str(uuid.uuid4())
  messages = [
    {"role": "system", "content": RESEARCH_SYSTEM_PROMPT},
    {"role": "user", "content": f"다음 주제를 조사해주세요: {topic}"}
  ]

  for _ in range(max_iterations):
    response = call_llm(
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
      notes = message.content
      return notes, trajectory

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

      trajectory.append((name, args, result))
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
  response = call_llm(
    trace_id=trace_id,
    model="gpt-5.6-luna",
    messages=messages,
    reasoning_effort="none",
    temperature=0.2
  )
  notes = response.choices[0].message.content

  return notes, trajectory


import re

def clean_url(url):
  """URL 끝에 딸려 온 문장부호를 제거하고 표기를 통일합니다."""
  return url.rstrip(".,;:]*").rstrip("/")

def check_citations(report, trajectory):
  """보고서에 인용된 URL을 실제로 읽었는지 확인합니다."""
  read_urls = {
    clean_url(args["url"])
    for name, args, result in trajectory
    if name == "read_webpage"
    and not result.startswith(("페이지를", "본문을"))  # 실패한 읽기 제외
  }
  cited_urls = {
    clean_url(u) for u in re.findall(r"https?://[^\s)\"']+", report)
  }
  unread = cited_urls - read_urls
  return {
    "passed": len(unread) == 0,
    "unread_citations": sorted(unread)
  }

def check_effort(trajectory, min_searches=2, min_reads=2):
  """조사가 충분히 이루어졌는지 확인합니다."""
  searches = sum(1 for name, _, _ in trajectory if name == "search_web")
  reads = sum(1 for name, _, _ in trajectory if name == "read_webpage")
  return {
    "passed": searches >= min_searches and reads >= min_reads,
    "searches": searches,
    "reads": reads
  }


RUBRIC_FORMAT = {
  "type": "json_schema",
  "json_schema": {
    "name": "rubric_scores",
    "strict": True,
    "schema": {
      "type": "object",
      "properties": {
        "grounded": {"type": "integer",
                     "description": "주장이 조사 내용에 근거함 (1~5)"},
        "structured": {"type": "integer",
                       "description": "요청한 구성을 따름 (1~5)"},
        "clear": {"type": "integer",
                  "description": "군더더기 없이 요점이 전달됨 (1~5)"},
        "reasons": {"type": "string",
                    "description": "각 점수의 근거 요약"}
      },
      "required": ["grounded", "structured", "clear", "reasons"],
      "additionalProperties": False
    }
  }
}

def judge_report(topic, notes, report):
  """루브릭으로 보고서를 채점합니다."""
  prompt = (
    "다음 보고서를 루브릭에 따라 1~5점으로 채점해주세요. "
    "점수는 보고서의 길이나 문장의 유창함이 아니라 "
    "루브릭의 기준만으로 판단하세요.\n\n"
    f"## 주제\n{topic}\n\n## 조사 노트\n{notes}\n\n"
    f"## 보고서\n{report}"
  )
  response = call_llm(
    model="gpt-5.6-luna",
    messages=[{"role": "user", "content": prompt}],
    response_format=RUBRIC_FORMAT,
    reasoning_effort="none",
    temperature=0
  )
  return json.loads(response.choices[0].message.content)


EVAL_TOPICS = [
  "중소 개발팀의 AI 코딩 도구 도입 효과",
  "전기차 배터리 재활용 기술의 현황",
  "원격 근무가 신입 개발자 성장에 미치는 영향",
]

def run_eval_suite(topics=EVAL_TOPICS):
  """평가 세트 전체를 실행하고 결과를 집계합니다."""
  results = []
  for topic in topics:
    notes, trajectory = run_research_traced(topic)
    report = write_report(topic, notes)

    result = {
      "topic": topic,
      "citations": check_citations(report, trajectory),
      "effort": check_effort(trajectory),
      "scores": judge_report(topic, notes, report),
    }
    results.append(result)

    print(f"\n[{topic}]")
    print(f"  인용 검증: {'통과' if result['citations']['passed'] else '실패'}")
    print(f"  조사 성실성: {'통과' if result['effort']['passed'] else '실패'} "
          f"(검색 {result['effort']['searches']}회, "
          f"읽기 {result['effort']['reads']}회)")
    print(f"  루브릭: 근거 {result['scores']['grounded']}, "
          f"구성 {result['scores']['structured']}, "
          f"명료 {result['scores']['clear']}")
  return results


# ---------------------------------------------------------------------------
# 회귀: 변경 앞의 관문
# ---------------------------------------------------------------------------

def rubric_avg(result):
  """루브릭 세 항목의 평균 점수를 계산합니다."""
  s = result["scores"]
  return (s["grounded"] + s["structured"] + s["clear"]) / 3

def compare_runs(baseline, candidate, score_drop=0.5):
  """변경 전후의 평가 결과를 비교합니다."""
  for base, cand in zip(baseline, candidate):
    b = base["citations"]["passed"] and base["effort"]["passed"]
    c = cand["citations"]["passed"] and cand["effort"]["passed"]
    if (b and not c) or rubric_avg(base) - rubric_avg(cand) >= score_drop:
      print(f"회귀 발견: {base['topic']}")
    elif not b and c:
      print(f"개선: {base['topic']}")


if __name__ == "__main__":
  run_eval_suite()  # [예제 보충]
