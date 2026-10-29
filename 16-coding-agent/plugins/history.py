"""히스토리 압축 훅 플러그인(13장 compact_history, 5장 summarize_history에서 가져옴).

16장 본문(308쪽): "13장에서 만든 compact_history 훅이 before_llm 시점에 그대로 동작합니다."
"""

from agent import hook, client  # [예제 보충] 훅이 쓰는 코어의 이름들

def summarize_history(messages, client, keep_recent=6):
  """오래된 대화 히스토리를 요약합니다.

  Args:
    messages: 전체 메시지 리스트
    client: OpenAI 클라이언트
    keep_recent: 최근 유지할 메시지 수
  """
  if len(messages) <= keep_recent + 2:  # system + 최근 메시지
    return messages

  system_msg = messages[0]
  cut = len(messages) - keep_recent
  # 도구 호출과 결과의 쌍이 경계에서 잘리지 않도록 보정
  while cut < len(messages) and messages[cut].get("role") == "tool":
    cut += 1
  old_messages = messages[1:cut]
  recent_messages = messages[cut:]

  # 오래된 대화 요약 요청
  summary_prompt = (
    "다음은 텍스트 어드벤처 게임의 이전 진행 내용입니다. "
    "핵심 사건과 발견한 것들을 간결하게 요약해주세요.\n\n"
  )
  for msg in old_messages:
    if msg["role"] == "user":
      summary_prompt += f"플레이어: {msg['content']}\n"
    elif msg["role"] == "assistant" and isinstance(msg.get("content"), str):
      summary_prompt += f"게임: {msg['content'][:200]}\n"

  summary_response = client.chat.completions.create(
    model="gpt-5.6-luna",
    messages=[{"role": "user", "content": summary_prompt}],
    reasoning_effort="none",
    temperature=0.3
  )
  summary = summary_response.choices[0].message.content

  # 요약본으로 교체
  summary_msg = {
    "role": "user",
    "content": f"[이전 게임 진행 요약]\n{summary}"
  }

  return [system_msg, summary_msg] + recent_messages

@hook("before_llm")
def compact_history(data):
  """대화가 길어지면 오래된 부분을 요약합니다 (5장의 기법)."""
  if len(data["messages"]) > 20:
    data["messages"] = summarize_history(data["messages"], client)
  return data
