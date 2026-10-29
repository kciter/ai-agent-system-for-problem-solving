"""15장 2단계: 12장 리서치 팀을 랭그래프로 선언한 그래프('리서치 팀을 그래프로').

실행: python step2_research_graph.py  (.env에 OPENAI_API_KEY 필요)
"""

from research_team import (  # [예제 보충] 12장에서 만든 함수들(research_team.py)
  plan_subtopics, run_workers, write_report, evaluate_report)

from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class ResearchState(TypedDict):
  topic: str
  subtopics: list
  notes: str      # 원본 조사 노트
  report: str
  problems: str   # 직전 검증에서 나온 문제점
  passed: bool
  rewrites: int

def plan_node(state):
  """주제를 하위 질문으로 분해합니다."""
  return {"subtopics": plan_subtopics(state["topic"])}

def research_node(state):
  """워커들이 병렬로 조사합니다."""
  notes = run_workers(state["subtopics"])
  combined = ""
  for sub, note in zip(state["subtopics"], notes):
    combined += f"## 하위 질문: {sub}\n{note}\n\n"
  return {"notes": combined}

def write_node(state):
  """조사 노트로 보고서를 작성합니다."""
  notes = state["notes"]
  if state.get("problems"):
    notes += f"\n\n## 이전 보고서의 문제점 (수정할 것)\n{state['problems']}"
  return {
    "report": write_report(state["topic"], notes),
    "rewrites": state["rewrites"] + 1
  }

def evaluate_node(state):
  """보고서를 검증합니다."""
  evaluation = evaluate_report(state["notes"], state["report"])
  if not evaluation["passed"]:
    return {"passed": False,
            "problems": "\n".join(evaluation["problems"])}
  return {"passed": True}

def should_rewrite(state):
  """검증 결과에 따라 재작성 여부를 결정합니다."""
  if state["passed"] or state["rewrites"] > 2:
    return END
  return "write"

graph = StateGraph(ResearchState)
graph.add_node("plan", plan_node)
graph.add_node("research", research_node)
graph.add_node("write", write_node)
graph.add_node("evaluate", evaluate_node)

graph.add_edge(START, "plan")
graph.add_edge("plan", "research")
graph.add_edge("research", "write")
graph.add_edge("write", "evaluate")
graph.add_conditional_edges("evaluate", should_rewrite)

app = graph.compile()

if __name__ == "__main__":
  result = app.invoke({"topic": "AI 에이전트 도입이 개발 조직에 미치는 영향",
                       "rewrites": 0})
  if not result["passed"]:
    print("경고: 검증을 통과하지 못한 보고서입니다. 확인이 필요합니다.")
  print(result["report"])
