"""승인 게이트 훅 플러그인(16장 '구현: 명령 실행과 승인 게이트')."""

from agent import hook  # [예제 보충]

DANGEROUS_PATTERNS = ["rm ", "sudo", "mv ", ">", "curl", "wget", "git push"]

@hook("before_tool")
def approve_commands(data):
  """명령 실행 도구는 사람의 승인을 거칩니다."""
  if data["name"] != "run_command" or data["blocked"]:
    return data

  command = data["args"].get("command", "")
  risky = any(p in command for p in DANGEROUS_PATTERNS)

  print(f"\n[명령 실행 요청] {command}")
  if risky:
    print("주의: 위험할 수 있는 명령입니다.")
  answer = input("실행하시겠습니까? (y/n) ")

  if answer.strip().lower() != "y":
    data["blocked"] = True
    data["result"] = "사용자가 명령 실행을 거부했습니다. 다른 방법을 검토하세요."
  return data
