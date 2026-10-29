"""13장 승인 게이트 훅."""

from agent import hook  # [예제 보충] 13장: 플러그인은 코어의 hook 데코레이터를 가져다 씁니다

REQUIRES_APPROVAL = {"send_email", "delete_file"}

@hook("before_tool")
def approve_dangerous_tools(data):
  """위험한 도구 실행 전에 사람의 승인을 받습니다."""
  if data["name"] in REQUIRES_APPROVAL and not data["blocked"]:
    print(f"[승인 요청] {data['name']} 실행: {data['args']}")
    answer = input("승인하시겠습니까? (y/n) ")
    if answer.strip().lower() != "y":
      data["blocked"] = True
      data["result"] = "사용자가 실행을 거부했습니다. 다른 방법을 검토하세요."
  return data
