"""플러그인: 웹 도구(search_web, read_webpage)를 등록합니다.

search_web의 등록 코드는 책 13장 '확장 지점 1: 도구 레지스트리'의 것이고, 함수 본문과
read_webpage는 7장의 코드를 그대로 가져왔습니다.
"""

from agent import tool  # [예제 보충] 플러그인은 agent 모듈의 데코레이터로 자신을 등록합니다(266쪽)

# 7장의 도구가 쓰는 라이브러리
import time
from ddgs import DDGS
import trafilatura


@tool(
  description="웹에서 검색합니다. 제목, 주소, 요약으로 이루어진 "
              "검색 결과 목록을 반환합니다. 자세한 내용이 필요하면 "
              "결과의 주소를 read_webpage로 읽어야 합니다.",
  parameters={
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "검색어. 구체적일수록 좋습니다."
      }
    },
    "required": ["query"]
  }
)
def search_web(query, max_results=5):
  """웹에서 검색하고 결과 목록을 문자열로 반환합니다."""
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


# [예제 보충] 책은 read_webpage의 등록 코드를 보여주지 않습니다(프로젝트 구조 266쪽).
# search_web과 같은 방식으로 7장 tools 배열의 설명과 파라미터를 옮겼습니다.
@tool(
  description="웹 페이지의 본문을 읽습니다. 검색 결과의 요약만으로 "
              "부족할 때, 출처로 인용할 내용을 확인할 때 사용합니다.",
  parameters={
    "type": "object",
    "properties": {
      "url": {
        "type": "string",
        "description": "읽을 페이지의 주소"
      }
    },
    "required": ["url"]
  }
)
def read_webpage(url):
  """웹 페이지의 본문을 추출하여 반환합니다."""
  html = trafilatura.fetch_url(url)
  if html is None:
    return "페이지를 가져올 수 없습니다. 다른 페이지를 시도해보세요."

  text = trafilatura.extract(html)
  if text is None:
    return "본문을 추출할 수 없습니다. 다른 페이지를 시도해보세요."

  return text[:4000]  # 지나치게 긴 본문은 잘라서 반환
