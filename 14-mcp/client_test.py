"""14장 MCP 클라이언트 테스트: 서버에 연결해 도구 목록을 받고 search_web을 호출합니다.

실행: python client_test.py (같은 디렉터리의 research_server.py를 자식 프로세스로 띄움)
"""

# client_test.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
  command="python",
  args=["research_server.py"]
)

async def main():
  async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
      # 초기화 핸드셰이크
      await session.initialize()

      # 서버가 제공하는 도구 목록 조회
      tool_list = await session.list_tools()
      print("서버가 제공하는 도구:")
      for t in tool_list.tools:
        print(f"- {t.name}: {t.description}")

      # 도구 호출
      result = await session.call_tool(
        "search_web",
        {"query": "Model Context Protocol"}
      )
      print(result.content[0].text)

if __name__ == "__main__":  # [예제 보충] import할 때 바로 실행되지 않도록
  asyncio.run(main())
