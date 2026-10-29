"""9장 보안: 개인정보 마스킹, 승인 게이트, 샌드박스.

프롬프트 인젝션 방어(wrap_external_data, 경계 표시를 쓰는 read_webpage)는 research_agent.py에 있습니다.
execute_tool이 쓰는 run_tool은 책이 "7장의 도구 분기처럼 이름에 따라 실제 함수를 호출하는
디스패처"라고 가정만 하므로, 7장의 분기를 그대로 옮겨 채웠습니다([예제 보충]).
"""

import re

def mask_pii(text):
  """텍스트에서 이메일과 전화번호를 마스킹합니다."""
  text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
                "[이메일]", text)
  text = re.sub(r"(?<!\d)01[016789]-?\d{3,4}-?\d{4}(?!\d)",
                "[전화번호]", text)
  return text


# 사람의 승인이 필요한 도구 목록
REQUIRES_APPROVAL = {"send_email", "delete_file"}

def execute_tool(name, args):
  """도구를 실행하되, 위험한 도구는 사람의 승인을 거칩니다."""
  if name in REQUIRES_APPROVAL:
    print(f"[승인 요청] {name} 실행: {args}")
    answer = input("승인하시겠습니까? (y/n) ")
    if answer.strip().lower() != "y":
      return "사용자가 실행을 거부했습니다. 다른 방법을 검토하세요."

  return run_tool(name, args)


# [예제 보충] 책: "run_tool은 7장의 도구 분기처럼 이름에 따라 실제 함수를 호출하는 디스패처라고 가정합니다."
from research_agent import search_web, read_webpage

def run_tool(name, args):
  """이름에 따라 실제 도구 함수를 호출합니다."""
  if name == "search_web":
    return search_web(**args)
  elif name == "read_webpage":
    return read_webpage(**args)
  else:
    return "알 수 없는 도구입니다."


import subprocess

def run_in_sandbox(command, workdir):
  """명령을 격리된 컨테이너 안에서 실행합니다."""
  result = subprocess.run(
    ["docker", "run", "--rm",
     "--network", "none",              # 네트워크 차단
     "-v", f"{workdir}:/workspace",    # 작업 디렉터리만 연결
     "-w", "/workspace",
     "python:3.12-slim",
     "timeout", "-k", "5", "55",       # 컨테이너 안의 시간 제한
     "bash", "-c", command],
    capture_output=True, text=True, timeout=60
  )
  return result.stdout + result.stderr
