"""15장 3단계: invoke 대신 stream으로 실행 과정 지켜보기.

실행: python step3_stream.py  (.env에 OPENAI_API_KEY 필요)
"""

from step2_research_graph import app  # [예제 보충] 2단계에서 만든 그래프

if __name__ == "__main__":
  for step in app.stream({"topic": "...", "rewrites": 0},
                         stream_mode="updates"):
    for node, update in step.items():
      print(f"[{node}] 갱신: {list(update.keys())}")
