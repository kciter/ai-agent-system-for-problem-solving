"""플러그인: 감사 로그 훅(after_tool)."""

from agent import hook  # [예제 보충] 책은 플러그인 파일의 import 줄을 보여주지 않습니다

@hook("after_tool")
def audit_tool_calls(data):
  """도구 호출을 감사 로그로 남깁니다."""
  status = "차단됨" if data["blocked"] else "실행 완료"
  print(f"[감사] {data['name']} {status}")
  return data
