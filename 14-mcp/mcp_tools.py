"""14장: MCP 서버의 도구를 13장의 등록부(TOOLS)에 올리는 어댑터.

register_mcp_tools는 책의 코드 그대로입니다. make_mcp_caller는 책이 구현을 일부러 생략한
함수라서(14장 본문 참고), 책의 설명대로 동작하는 최소 구현을 [예제 보충]으로 넣었습니다.
"""

import asyncio  # [예제 보충]

from agent import TOOLS  # [예제 보충] 13장의 등록부


def register_mcp_tools(session, tool_list):
  """MCP 서버의 도구들을 13장의 등록부에 등록합니다."""
  for t in tool_list.tools:
    TOOLS[t.name] = {
      "func": make_mcp_caller(session, t.name),
      "schema": {
        "type": "function",
        "function": {
          "name": t.name,
          "description": t.description or "",
          "parameters": t.input_schema  # 이미 JSON 스키마 형식
        }
      }
    }


# [예제 보충] 책은 make_mcp_caller의 구현을 생략합니다. 본문의 설명 그대로
# "도구 이름을 받아 session.call_tool을 대신 호출해주는 함수"이고, 비동기 호출을
# 동기로 감싸는 배관만 넣었습니다. 본문이 이 함수의 일로 말하지 않은 결과 변환
# (CallToolResult를 문자열로)은 하지 않습니다(README의 '알려진 문제' 참고).
def make_mcp_caller(session, name):
  """session.call_tool(name, args)를 동기 함수처럼 부를 수 있게 감쌉니다.

  register_mcp_tools는 세션이 열려 있는 이벤트 루프 안에서 호출하고,
  13장의 동기 코어 루프(run_agent)는 다른 스레드에서 실행해야 합니다
  (main.py의 asyncio.to_thread 참고).
  """
  loop = asyncio.get_running_loop()  # 세션이 동작하는 이벤트 루프

  def call(**args):
    future = asyncio.run_coroutine_threadsafe(session.call_tool(name, args), loop)
    return future.result()

  return call
