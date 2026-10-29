"""플러그인: 히스토리 요약 훅(before_llm).

책 13장 '확장 지점 2: 훅'(261~262쪽)의 compact_history 훅입니다. 책의 프로젝트 구조(266쪽)에는 없지만
본문에서 플러그인으로 옮기는 훅이므로 플러그인 파일로 두었습니다.
summarize_history는 5장의 함수를 그대로 가져왔습니다(텍스트 어드벤처 게임용 프롬프트 포함).
"""

from agent import hook, client  # [예제 보충] 훅 데코레이터와 8장의 client


# 5장의 summarize_history (5장에서 가져옴)
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
