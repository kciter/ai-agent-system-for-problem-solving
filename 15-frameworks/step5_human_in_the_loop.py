"""15장 5단계: interrupt와 Command로 사람의 승인을 받는 그래프(휴먼 인 더 루프).

본문(290쪽)의 전제대로, should_rewrite를 새 내용으로 바꾼 뒤 그래프 구성을 처음부터
다시 실행합니다. 이미 조건 엣지를 등록한 그래프(2단계의 graph)에 approve 노드만
덧붙이면 옛 should_rewrite로 분기해 승인 노드를 조용히 건너뜁니다.

실행: python step5_human_in_the_loop.py  (.env에 OPENAI_API_KEY 필요)
"""

# [예제 보충] 2단계와 4단계에서 쓰던 이름들
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from step2_research_graph import (
  ResearchState, plan_node, research_node, write_node, evaluate_node)

from langgraph.types import interrupt, Command

def approve_node(state):
  """보고서를 내보내기 전에 사람의 승인을 받습니다."""
  answer = interrupt(
    f"보고서를 승인하시겠습니까?\n\n{state['report'][:500]}"
  )
  return {} if answer == "y" else {"passed": False}

def should_rewrite(state):  # 기존 함수를 이 내용으로 교체
  if state["passed"]:
    return "approve"        # 통과하면 승인 노드로
  if state["rewrites"] > 2:
    return END
  return "write"

# [예제 보충] 본문(290쪽)의 전제: 함수 정의를 고친 뒤 그래프 구성을 처음부터 다시 실행합니다.
# 아래는 2단계의 그래프 구성 코드 그대로이며, 조건 엣지에는 위의 새 should_rewrite가 등록됩니다.
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

# evaluate 통과 후 approve 노드를 거치도록 그래프에 연결
graph.add_node("approve", approve_node)
graph.add_edge("approve", END)

app = graph.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "research-001"}}  # [예제 보충] 4단계의 config

if __name__ == "__main__":
  # 실행하면 approve 노드에서 멈추고, interrupt에 담은 내용이 반환됨
  result = app.invoke({"topic": "...", "rewrites": 0}, config=config)
  print(result["__interrupt__"][0].value)  # [예제 보충] 멈춘 지점에서 사람에게 보여줄 내용

  # 사람이 확인한 뒤 재개 (몇 분 뒤든 며칠 뒤든(DB 체크포인터 사용 시))
  result = app.invoke(Command(resume="y"), config=config)
  print(result["report"])  # [예제 보충] 결과 확인용
