"""감사 로그 훅 플러그인(13장에서 가져옴)."""

from agent import hook  # [예제 보충]

@hook("after_tool")
def audit_tool_calls(data):
  """도구 호출을 감사 로그로 남깁니다."""
  status = "차단됨" if data["blocked"] else "실행 완료"
  print(f"[감사] {data['name']} {status}")
  return data
