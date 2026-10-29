"""코딩 도구 플러그인: 작업 디렉터리 울타리(safe_path)와 여섯 도구.

16장 '구현: 안전한 파일 도구'와 '구현: 명령 실행과 승인 게이트'의 도구 코드입니다.
"""

from agent import tool  # [예제 보충] 13장 방식: 플러그인은 코어의 데코레이터로 등록합니다

import os

WORKSPACE = os.path.realpath("workspace")

def safe_path(path):
  """작업 디렉터리 안의 경로인지 확인하고 실제 경로를 돌려줍니다."""
  full = os.path.realpath(os.path.join(WORKSPACE, path))
  if os.path.commonpath([full, WORKSPACE]) != WORKSPACE:
    raise ValueError("작업 디렉터리 밖의 경로에는 접근할 수 없습니다.")
  return full

@tool(
  description="파일의 내용을 줄 번호와 함께 읽습니다. 파일이 길면 "
              "start_line과 max_lines로 원하는 부분만 읽으세요. "
              "경로는 작업 디렉터리 기준입니다.",
  parameters={
    "type": "object",
    "properties": {
      "path": {"type": "string", "description": "읽을 파일 경로"},
      "start_line": {"type": "integer",
                     "description": "읽기 시작할 줄 번호 (기본 1)"},
      "max_lines": {"type": "integer",
                    "description": "최대 몇 줄을 읽을지 (기본 200)"}
    },
    "required": ["path"]
  }
)
def read_file(path, start_line=1, max_lines=200):
  """파일 내용을 줄 번호와 함께 문자열로 반환합니다."""
  try:
    start_line = max(1, start_line)  # 음수/0 방어
    with open(safe_path(path), encoding="utf-8") as f:
      lines = f.readlines()
    end = min(len(lines), start_line - 1 + max_lines)
    numbered = [f"{i + 1}: {lines[i].rstrip()}"
                for i in range(start_line - 1, end)]
    header = f"(전체 {len(lines)}줄 중 {start_line}~{end}줄)\n"
    return header + "\n".join(numbered)
  except Exception as e:
    return f"파일을 읽을 수 없습니다: {e}"

@tool(
  description="작업 디렉터리의 텍스트 파일들에서 키워드가 포함된 줄을 "
              "찾습니다. 어느 파일을 봐야 할지 모를 때 먼저 사용하세요.",
  parameters={
    "type": "object",
    "properties": {
      "keyword": {"type": "string", "description": "찾을 키워드"}
    },
    "required": ["keyword"]
  }
)
def search_code(keyword):
  """키워드가 포함된 파일과 줄 번호 목록을 반환합니다."""
  matches = []
  for root, _, files in os.walk(WORKSPACE):
    for name in sorted(files):
      full = os.path.join(root, name)
      # 심볼릭 링크 등으로 작업 디렉터리를 벗어나는 파일은 건너뜀
      if os.path.commonpath([os.path.realpath(full), WORKSPACE]) != WORKSPACE:
        continue
      rel = os.path.relpath(full, WORKSPACE)
      try:
        with open(full, encoding="utf-8") as f:
          for i, line in enumerate(f, 1):
            if keyword in line:
              matches.append(f"{rel}:{i}: {line.strip()}")
              if len(matches) >= 50:
                return ("\n".join(matches)
                        + "\n(결과가 많아 50개에서 멈췄습니다)")
      except (UnicodeDecodeError, OSError):
        continue  # 바이너리 파일 등은 건너뜀
  return "\n".join(matches) if matches else "검색 결과가 없습니다."

@tool(
  description="파일에서 old_text를 찾아 new_text로 교체합니다. "
              "old_text는 파일 안에서 딱 한 번만 나타나도록 충분히 "
              "길게 지정하세요. 코드 수정에는 이 도구를 사용하세요.",
  parameters={
    "type": "object",
    "properties": {
      "path": {"type": "string", "description": "수정할 파일 경로"},
      "old_text": {"type": "string", "description": "교체될 기존 코드"},
      "new_text": {"type": "string", "description": "새로 들어갈 코드"}
    },
    "required": ["path", "old_text", "new_text"]
  }
)
def edit_file(path, old_text, new_text):
  """파일의 일부를 교체하고 결과를 문자열로 반환합니다."""
  try:
    full = safe_path(path)
    with open(full, encoding="utf-8") as f:
      content = f.read()
    count = content.count(old_text)
    if count == 0:
      return ("old_text를 파일에서 찾지 못했습니다. "
              "read_file로 현재 내용을 다시 확인하세요.")
    if count > 1:
      return (f"old_text가 파일에 {count}번 나타나 어느 것인지 알 수 "
              "없습니다. 앞뒤 줄을 포함해 더 길게 지정하세요.")
    with open(full, "w", encoding="utf-8") as f:
      f.write(content.replace(old_text, new_text))
    return f"{path}를 수정했습니다."
  except Exception as e:
    return f"파일을 수정할 수 없습니다: {e}"

@tool(
  description="새 파일을 만들거나 파일 전체를 교체합니다. 기존 파일의 "
              "일부만 고칠 때는 write_file이 아니라 edit_file을 쓰세요.",
  parameters={
    "type": "object",
    "properties": {
      "path": {"type": "string", "description": "쓸 파일 경로"},
      "content": {"type": "string", "description": "파일에 쓸 전체 내용"}
    },
    "required": ["path", "content"]
  }
)
def write_file(path, content):
  """파일에 내용을 쓰고 결과를 문자열로 반환합니다."""
  try:
    full = safe_path(path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
      f.write(content)
    return f"{path}에 저장했습니다."
  except Exception as e:
    return f"파일을 쓸 수 없습니다: {e}"

@tool(
  description="디렉터리의 파일 목록을 봅니다. 경로는 작업 디렉터리 "
              "기준이며, 생략하면 작업 디렉터리 전체를 봅니다.",
  parameters={
    "type": "object",
    "properties": {
      "path": {"type": "string", "description": "볼 디렉터리 경로"}
    },
    "required": []
  }
)
def list_files(path="."):
  """디렉터리의 파일과 폴더 목록을 문자열로 반환합니다."""
  try:
    entries = os.listdir(safe_path(path))
    return "\n".join(sorted(entries)) if entries else "(비어 있음)"
  except Exception as e:
    return f"목록을 볼 수 없습니다: {e}"

import subprocess

@tool(
  description="셸 명령을 작업 디렉터리에서 실행하고 출력을 반환합니다. "
              "코드 실행이나 테스트에 사용하세요.",
  parameters={
    "type": "object",
    "properties": {
      "command": {"type": "string", "description": "실행할 셸 명령"}
    },
    "required": ["command"]
  }
)
def run_command(command):
  """셸 명령을 작업 디렉터리에서 실행하고 결과를 반환합니다."""
  try:
    result = subprocess.run(
      command,
      shell=True,
      cwd=WORKSPACE,        # 작업 디렉터리에서 실행
      capture_output=True,
      text=True,
      timeout=30            # 무한 실행 방지
    )
    output = result.stdout + result.stderr
    return output if output else "(출력 없음)"
  except subprocess.TimeoutExpired:
    return "명령이 시간 초과되었습니다 (30초)."
  except Exception as e:
    return f"명령 실행 중 오류: {e}"
