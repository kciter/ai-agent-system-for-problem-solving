"""3장 '기본 설정 코드'. 환경 변수를 불러오고 오픈AI 클라이언트를 만듭니다.

실행: python agent.py  → "AI 에이전트 시작"
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# 환경 변수 로드
load_dotenv()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def main():
  print("AI 에이전트 시작")

if __name__ == "__main__":
  main()
