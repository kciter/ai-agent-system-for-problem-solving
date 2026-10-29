"""12장 남은 패턴: 토론.

제안자와 비판자가 반박을 주고받아 결론을 다듬는 최소형 토론 패턴입니다.
call_llm은 research_team.py에 있는 8장의 신뢰성 계층을 씁니다.

책과 다른 점: 마지막 실행 줄 print(debate(...))를
`if __name__ == "__main__":` 아래로 옮겼습니다.

실행: python debate.py  (.env에 OPENAI_API_KEY 필요)
"""

from research_team import call_llm  # [예제 보충] 8장의 call_llm(재시도와 로깅)


def debate(question, rounds=2):
  """제안자와 비판자가 반박을 주고받아 결론을 다듬습니다."""
  proposal = call_llm(
    model="gpt-5.6-luna",
    messages=[{"role": "user", "content":
      f"다음 질문에 대한 방안을 근거와 함께 제안해주세요.\n\n{question}"}],
    reasoning_effort="none",
    temperature=0.3
  ).choices[0].message.content

  for _ in range(rounds):
    critique = call_llm(
      model="gpt-5.6-luna",
      messages=[{"role": "user", "content":
        "다음 제안의 약점, 반례, 놓친 전제를 찾아 비판해주세요. "
        "동의하는 부분은 짧게 넘기고 문제에 집중하세요.\n\n"
        f"## 질문\n{question}\n\n## 제안\n{proposal}"}],
      reasoning_effort="none",
      temperature=0.3
    ).choices[0].message.content

    proposal = call_llm(
      model="gpt-5.6-luna",
      messages=[{"role": "user", "content":
        "비판을 반영해 제안을 보완해주세요. 타당한 비판은 수용해 "
        "수정하고, 아니라고 판단하면 근거를 들어 반박을 남기세요.\n\n"
        f"## 질문\n{question}\n\n## 제안\n{proposal}\n\n## 비판\n{critique}"}],
      reasoning_effort="none",
      temperature=0.3
    ).choices[0].message.content

  return proposal


if __name__ == "__main__":
  print(debate("에이전트의 대화 히스토리 저장소로 SQLite와 PostgreSQL 중 "
               "무엇을 쓸 것인가?"))
