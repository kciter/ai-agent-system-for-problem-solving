"""14장 MCP 서버: 7장의 웹 검색과 페이지 읽기 도구를 MCP 도구로 제공합니다.

책의 코드 그대로입니다. 실행: python research_server.py (stdio로 연결을 기다림)
"""

# research_server.py
import time
import trafilatura
from ddgs import DDGS
from mcp.server import MCPServer

mcp = MCPServer("research-tools")

@mcp.tool()
def search_web(query: str, max_results: int = 5) -> str:
  """웹에서 검색합니다. 제목, 주소, 요약으로 이루어진 검색 결과
  목록을 반환합니다. 자세한 내용이 필요하면 결과의 주소를
  read_webpage로 읽어야 합니다."""
  try:
    results = DDGS().text(query, max_results=max_results)
  except Exception as e:
    return f"검색 중 오류가 발생했습니다: {e}"
  if not results:
    return "검색 결과가 없습니다. 다른 검색어를 시도해보세요."
  lines = []
  for r in results:
    lines.append(
      f"- 제목: {r['title']}\n  주소: {r['href']}\n  요약: {r['body']}"
    )
  time.sleep(1)
  return "\n".join(lines)

@mcp.tool()
def read_webpage(url: str) -> str:
  """웹 페이지의 본문을 읽습니다. 검색 결과의 요약만으로
  부족할 때, 출처로 인용할 내용을 확인할 때 사용합니다."""
  html = trafilatura.fetch_url(url)
  if html is None:
    return "페이지를 가져올 수 없습니다. 다른 페이지를 시도해보세요."
  text = trafilatura.extract(html)
  if text is None:
    return "본문을 추출할 수 없습니다. 다른 페이지를 시도해보세요."
  return text[:4000]

if __name__ == "__main__":
  mcp.run()  # 기본 전송 방식은 stdio
