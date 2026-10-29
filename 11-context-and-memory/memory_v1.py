"""11장 장기 기억의 첫 버전: 기억을 텍스트 파일에 남깁니다.

책 11장 '장기 기억: 세션을 넘어서'의 코드입니다. 다음 절에서 임베딩 검색 버전(memory.py)으로
다시 만들기 때문에 따로 두었습니다. LLM을 호출하지 않습니다.
"""

MEMORY_FILE = "memories.txt"

def remember(fact):
  """기억할 가치가 있는 사실을 파일에 기록합니다."""
  with open(MEMORY_FILE, "a", encoding="utf-8") as f:
    f.write(fact + "\n")
  return f"기억했습니다: {fact}"

def load_memories():
  """저장된 기억 전체를 읽어옵니다."""
  try:
    with open(MEMORY_FILE, encoding="utf-8") as f:
      return f.read()
  except FileNotFoundError:
    return ""
