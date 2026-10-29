"""13장 감사 로그 훅."""

from agent import hook  # [예제 보충] 13장: 플러그인은 코어의 hook 데코레이터를 가져다 씁니다

@hook("after_tool")
def audit_tool_calls(data):
  """도구 호출을 감사 로그로 남깁니다."""
  status = "차단됨" if data["blocked"] else "실행 완료"
  print(f"[감사] {data['name']} {status}")
  return data
