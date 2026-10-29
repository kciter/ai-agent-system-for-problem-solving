"""15장 4단계: 체크포인터를 켜고 thread_id로 실행하기('실행을 맡기면 생기는 것들').

실행: python step4_checkpoint.py  (.env에 OPENAI_API_KEY 필요)
"""

from step2_research_graph import graph  # [예제 보충] 2단계에서 만든 그래프

from langgraph.checkpoint.memory import InMemorySaver

app = graph.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "research-001"}}

if __name__ == "__main__":
  result = app.invoke({"topic": "...", "rewrites": 0}, config=config)
  print(result["report"])  # [예제 보충] 결과 확인용
