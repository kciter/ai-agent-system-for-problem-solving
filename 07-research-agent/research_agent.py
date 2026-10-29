"""7장 자동 리서치 에이전트.

책 7장의 코드를 순서대로 이어 붙였습니다. 책과 다른 점은 마지막 실행 줄을
`if __name__ == "__main__":` 아래로 옮긴 것 하나입니다(다른 파일에서 import할 때 바로 실행되지 않도록).

실행: python research_agent.py  (.env에 OPENAI_API_KEY 필요)
"""

import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()


import time
from ddgs import DDGS

def search_web(query, max_results=5):
  """웹에서 검색하고 결과 목록을 문자열로 반환합니다."""
  try:
    results = DDGS().text(query, max_results=max_results)
  except Exception as e:
    return f"검색 중 오류가 발생했습니다: {e}"

  if not results:
    return "검색 결과가 없습니다. 다른 검색어를 시도해보세요."

  lines = []
  for r in results:
    lines.append(
      f"- 제목: {r['title']}\n"
      f"  주소: {r['href']}\n"
      f"  요약: {r['body']}"
    )
  time.sleep(1)  # 연속 검색 시 차단을 피하기 위한 지연
  return "\n".join(lines)


import trafilatura

def read_webpage(url):
  """웹 페이지의 본문을 추출하여 반환합니다."""
  html = trafilatura.fetch_url(url)
  if html is None:
    return "페이지를 가져올 수 없습니다. 다른 페이지를 시도해보세요."

  text = trafilatura.extract(html)
  if text is None:
    return "본문을 추출할 수 없습니다. 다른 페이지를 시도해보세요."

  return text[:4000]  # 지나치게 긴 본문은 잘라서 반환


tools = [
  {
    "type": "function",
    "function": {
      "name": "search_web",
      "description": "웹에서 검색합니다. 제목, 주소, 요약으로 이루어진 "
                     "검색 결과 목록을 반환합니다. 자세한 내용이 필요하면 "
                     "결과의 주소를 read_webpage로 읽어야 합니다.",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "검색어. 구체적일수록 좋습니다."
          },
          "max_results": {
            "type": "integer",
            "description": "가져올 검색 결과 수 (기본 5)"
          }
        },
        "required": ["query"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "read_webpage",
      "description": "웹 페이지의 본문을 읽습니다. 검색 결과의 요약만으로 "
                     "부족할 때, 출처로 인용할 내용을 확인할 때 사용합니다.",
      "parameters": {
        "type": "object",
        "properties": {
          "url": {
            "type": "string",
            "description": "읽을 페이지의 주소"
          }
        },
        "required": ["url"]
      }
    }
  }
]


RESEARCH_SYSTEM_PROMPT = """당신은 주어진 주제를 조사하는 리서치 에이전트입니다.

## 작업 방식
1. 주제를 파악하고 무엇을 검색할지 계획하세요.
2. search_web으로 검색하고, 중요해 보이는 페이지는 read_webpage로
   직접 읽으세요. 검색 결과의 짧은 요약만 보고 판단하지 마세요.
3. 하나의 출처에 의존하지 말고, 서로 다른 출처를 3개 이상 확인하세요.
4. 정보가 충분히 모였다고 판단되면 도구 호출을 멈추고,
   수집한 정보를 정리해서 응답하세요.

## 조사 노트 규칙
- 수집한 정보를 정리할 때는 각 정보를 어느 페이지(URL)에서
  얻었는지 반드시 함께 기록하세요.
- 페이지에서 확인한 내용만 기록하세요. 추측이나 사전 지식으로
  내용을 보충하지 마세요.
"""

def run_research(topic, max_iterations=10):
  """주제를 조사하고 출처가 달린 조사 노트를 반환합니다."""
  messages = [
    {"role": "system", "content": RESEARCH_SYSTEM_PROMPT},
    {"role": "user", "content": f"다음 주제를 조사해주세요: {topic}"}
  ]

  for _ in range(max_iterations):
    response = client.chat.completions.create(
      model="gpt-5.6-luna",
      messages=messages,
      tools=tools,
      reasoning_effort="none",
      temperature=0.2
    )
    message = response.choices[0].message
    messages.append(message)

    # 도구 호출이 없으면 조사 완료
    if not message.tool_calls:
      return message.content

    # 도구 호출 처리
    for tool_call in message.tool_calls:
      args = json.loads(tool_call.function.arguments)
      name = tool_call.function.name
      print(f"[도구 호출] {name}: {args}")

      try:
        if name == "search_web":
          result = search_web(**args)
        elif name == "read_webpage":
          result = read_webpage(**args)
        else:
          result = "알 수 없는 도구입니다."
      except Exception as e:
        result = f"도구 호출 중 오류가 발생했습니다: {e}"

      messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result
      })

  # 반복 상한 도달: 지금까지 모은 정보로 마무리
  messages.append({
    "role": "user",
    "content": "조사를 마무리하고 지금까지 수집한 정보를 정리해주세요."
  })
  response = client.chat.completions.create(
    model="gpt-5.6-luna",
    messages=messages,
    reasoning_effort="none",
    temperature=0.2
  )
  return response.choices[0].message.content


def write_report(topic, research_notes):
  """조사 노트를 바탕으로 보고서를 작성합니다."""
  prompt = (
    f"다음은 '{topic}'에 대한 조사 노트입니다. "
    "이를 바탕으로 마크다운 형식의 보고서를 작성해주세요.\n\n"
    "## 작성 규칙\n"
    "- 개요, 주요 내용, 시사점, 참고 자료 순으로 구성하세요.\n"
    "- 조사 노트에 있는 내용만 사용하세요. 노트에 없는 사실을 "
    "추가하지 마세요.\n"
    "- 주요 내용의 각 항목에는 근거가 된 출처(URL)를 표기하세요.\n"
    "- 참고 자료 절에 사용한 모든 출처를 나열하세요.\n\n"
    f"## 조사 노트\n{research_notes}"
  )
  response = client.chat.completions.create(
    model="gpt-5.6-luna",
    messages=[{"role": "user", "content": prompt}],
    reasoning_effort="none",
    temperature=0.3
  )
  return response.choices[0].message.content

def research_agent(topic):
  """주제를 조사하고 보고서를 반환합니다."""
  print(f"주제: {topic}\n")
  notes = run_research(topic)
  print("\n조사 완료. 보고서를 작성합니다...\n")
  report = write_report(topic, notes)
  return report


if __name__ == "__main__":
  print(research_agent("중소 규모 개발팀의 AI 코딩 도구 도입 현황과 효과"))
