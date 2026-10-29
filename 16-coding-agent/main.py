"""16장 코딩 에이전트 실행 파일.

실행: python main.py  (이 디렉터리에서, .env에 OPENAI_API_KEY 필요)
작업 디렉터리는 ./workspace 입니다.
"""

from agent import coding_agent  # [예제 보충] 13장 구조대로 실행 코드는 agent.py 밖에 둡니다

if __name__ == "__main__":
  coding_agent()
