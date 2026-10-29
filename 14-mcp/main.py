"""[예제 보충] MCP 서버의 도구로 13장의 에이전트를 실행하는 코드.

책은 이 조립 코드를 보여주지 않습니다(14장 본문: "지면에서는 생략합니다").
13장 main.py와 14장 client_test.py, register_mcp_tools를 이어 붙인 것입니다.

실행: python main.py (.env에 OPENAI_API_KEY 필요, research_server.py를 자식 프로세스로 띄움)
"""

import asyncio

from mcp import ClientSession
from mcp.client.stdio import stdio_client

from agent import load_plugins, run_agent
from client_test import server_params  # client_test.py와 같은 서버 실행 설정
from mcp_tools import register_mcp_tools


async def main():
  load_plugins()  # plugins/approval.py, plugins/audit.py
  async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
      await session.initialize()
      tool_list = await session.list_tools()
      register_mcp_tools(session, tool_list)

      # 13장의 코어 루프는 동기 함수라서 이벤트 루프를 막지 않도록 다른 스레드에서 실행합니다.
      answer = await asyncio.to_thread(
        run_agent,
        user_message="MCP(Model Context Protocol)가 무엇인지 조사해주세요.",
        system_prompt="당신은 주어진 주제를 조사하는 리서치 에이전트입니다."
      )
  print(answer)


if __name__ == "__main__":
  asyncio.run(main())
