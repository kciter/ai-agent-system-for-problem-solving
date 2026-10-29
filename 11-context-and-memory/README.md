# 11장 컨텍스트와 메모리

대화가 길어지면 구조화된 요약으로 압축하는 함수, 임베딩으로 의미가 가까운 기억을 찾는 기억 저장소, 같은 저장소로 문서를 찾아 답하는 RAG 예제입니다.

## 파일

| 파일 | 내용 | 책의 위치 |
|---|---|---|
| `memory_v1.py` | 기억을 텍스트 파일(`memories.txt`)에 남기는 첫 버전: `remember`, `load_memories` | 11장 '장기 기억: 세션을 넘어서' |
| `memory.py` | 8장 신뢰성 계층(`client`, `call_llm`), `compact_if_needed`, `embed`, `cosine_similarity`, 의미 검색 기억 저장소(`load_memory_store`, `remember`, `recall`), `answer_with_docs`, `split_into_chunks`, 기억을 시험하는 실행 코드 | 11장 '압축 구현하기'부터 '기억에서 지식으로: RAG'까지 |

## 책과 다른 점

- `memory.py` 앞부분의 `client`, `call_with_retry`, `call_llm`, `write_log`는 8장 코드를 그대로 가져왔습니다. 11장의 `compact_if_needed`와 `answer_with_docs`가 `call_llm`을, `embed`가 `client`를 쓰기 때문입니다. `client`는 8장의 최종 설정 `OpenAI(timeout=30.0, max_retries=0)`이고, `.env`는 7장처럼 `load_dotenv()`로 읽습니다.
- 기억을 시험하는 코드(`remember` 네 번과 `print(recall(...))`)는 책에서는 `recall` 바로 뒤에 나오지만, 파일 끝의 `if __name__ == "__main__":` 아래로 옮겼습니다. 다른 파일에서 이 파일을 import할 때 바로 실행되지 않게 하기 위해서입니다.
- 기억 저장소의 첫 버전(`memories.txt`)과 다시 만든 버전(`memories.json`)은 함수 이름(`remember`)이 같아서 파일을 나눴습니다.

## 실행

```bash
uv sync
echo "OPENAI_API_KEY=sk-..." > .env
uv run memory.py
```

현재 디렉터리에 `memories.json`(기억)과 `llm_calls.jsonl`(8장의 호출 로그)이 생깁니다. 실행할 때마다 기억 네 개가 다시 추가되므로, 처음부터 다시 해보려면 `memories.json`을 지우세요. 실제 임베딩으로 실행하면 두 번째 줄은 책과 다를 수 있습니다.
