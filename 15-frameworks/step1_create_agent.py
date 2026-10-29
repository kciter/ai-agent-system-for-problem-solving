"""15장 1단계: create_agent로 만든 리서치 에이전트('에이전트 루프를 몇 줄로').

실행: python step1_create_agent.py  (.env에 OPENAI_API_KEY 필요)
"""

from dotenv import load_dotenv  # [예제 보충] 3장처럼 .env에서 OPENAI_API_KEY를 읽습니다
load_dotenv()  # [예제 보충]

# [예제 보충] 도구 본문(7장)이 쓰는 라이브러리와 7장의 시스템 프롬프트
import time
import trafilatura
from ddgs import DDGS
from research_team import RESEARCH_SYSTEM_PROMPT

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

@tool
def search_web(query: str, max_results: int = 5) -> str:
  """웹에서 검색합니다. 제목, 주소, 요약으로 이루어진 검색 결과
  목록을 반환합니다. 자세한 내용이 필요하면 결과의 주소를
  read_webpage로 읽어야 합니다."""
  # 함수 본문은 7장과 동일
  try:
    results = DDGS().text(query, max_results=max_results)
  except Exception as e:
    return f"검색 중 오류가 발생했습니다: {e}"

  if not results:
    return "검색 결과가 없습니다. 다른 검색어를 시도해보세요."

  lines = []
  for r in results:
    lines.append(
      f"- 제목: {r['title']}\n"
      f"  주소: {r['href']}\n"
      f"  요약: {r['body']}"
    )
  time.sleep(1)  # 연속 검색 시 차단을 피하기 위한 지연
  return "\n".join(lines)

@tool
def read_webpage(url: str) -> str:
  """웹 페이지의 본문을 읽습니다. 검색 결과의 요약만으로
  부족할 때, 출처로 인용할 내용을 확인할 때 사용합니다."""
  # [예제 보충] 7장 read_webpage의 본문
  html = trafilatura.fetch_url(url)
  if html is None:
    return "페이지를 가져올 수 없습니다. 다른 페이지를 시도해보세요."

  text = trafilatura.extract(html)
  if text is None:
    return "본문을 추출할 수 없습니다. 다른 페이지를 시도해보세요."

  return text[:4000]  # 지나치게 긴 본문은 잘라서 반환

agent = create_agent(
  model=ChatOpenAI(model="gpt-5.6-luna", reasoning_effort="none"),
  tools=[search_web, read_webpage],
  system_prompt=RESEARCH_SYSTEM_PROMPT
)

if __name__ == "__main__":
  result = agent.invoke({
    "messages": [
      {"role": "user", "content": "다음 주제를 조사해주세요: ..."}
    ]
  })
  print(result["messages"][-1].content)

  # 반환된 대화 기록을 열어보기 (책의 두 번째 블록)
  for m in result["messages"]:
    print(type(m).__name__, "-", str(m.content)[:40])
