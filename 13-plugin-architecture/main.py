"""13장: 실행 파일. 플러그인을 불러오고 에이전트를 호출합니다.

agent.py가 있는 프로젝트 루트에서 실행하세요: python main.py
(.env에 OPENAI_API_KEY 필요)
"""

from agent import load_plugins, run_agent, apply_skill  # [예제 보충] 책은 import 줄을 보여주지 않습니다

load_plugins()

answer = run_agent(
  user_message=apply_skill(
    "competitor-research",
    "A사의 최근 동향을 조사해주세요."
  ),
  system_prompt="당신은 주어진 주제를 조사하는 리서치 에이전트입니다. ..."
)
print(answer)
