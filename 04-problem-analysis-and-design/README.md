# 4장 문제 이해와 설계 결정: Queens 퍼즐 생성기

Queens 퍼즐을 규칙 기반 코드로 검증하고, 그 검증을 쓰는 두 가지 생성 에이전트(전부 LLM에게 맡긴 첫 번째 구현, 역할을 다시 나눈 두 번째 구현)를 실행해 볼 수 있습니다.

## 파일

| 파일 | 내용 | 책의 위치 |
|---|---|---|
| `queens_verify.py` | `validate_solution`, `solve_queens`, `are_regions_connected`, `verify_puzzle` | 4장 '검증 코드 구현' |
| `generator_v1.py` | `SYSTEM_PROMPT`, `verify_puzzle` 도구 정의, `generate_queens_puzzle`, 실행 코드 | '첫 번째 구현: 전부 LLM에게 맡기기', '생각처럼 되지 않는다' |
| `generator_v2.py` | `generate_solution`, `DESIGNER_PROMPT`, `verify_design`, `generate_queens_puzzle_v2`, 실행 코드 | '두 번째 구현: 역할을 다시 나누다' |

## 책과 다른 점

- 책은 한 파일에 이어서 쓰는 흐름이지만, 두 구현을 따로 실행할 수 있게 검증 코드(`queens_verify.py`)와 두 구현(`generator_v1.py`, `generator_v2.py`)을 나눴습니다. 그래서 다음 줄을 보충했습니다. 모두 `# [예제 보충]`으로 표시했습니다.
  - 두 구현 파일의 `from queens_verify import verify_puzzle`
  - `generator_v2.py` 앞부분의 설정(`import json`, `from openai import OpenAI`, `client = OpenAI()`). 첫 번째 구현에 있던 줄을 그대로 다시 썼습니다.
- 본문의 "환경 설정은 3장과 같이 .env 파일의 API 키를 load_dotenv로 불러온다고 가정합니다"에 따라 두 구현 파일에 `load_dotenv()`를 넣었습니다(`# [예제 보충]`).
- 실행 코드(`result = generate_queens_puzzle(size=5)`와 `result = generate_queens_puzzle_v2(size=5)`로 시작하는 블록)를 `if __name__ == "__main__":` 아래로 옮겼습니다. 다른 파일에서 import할 때 바로 실행되지 않게 하기 위해서입니다.

## 실행

```bash
uv sync
echo "OPENAI_API_KEY=sk-..." > .env
uv run generator_v1.py  # 첫 번째 구현. 책의 설명처럼 대부분 '생성 실패'로 끝납니다.
uv run generator_v2.py  # 두 번째 구현. 정답 배치가 난수라 매번 다른 퍼즐이 나옵니다.
```

검증 코드는 API 키 없이 바로 써볼 수 있습니다.

```bash
uv run python -c "from queens_verify import verify_puzzle; print(verify_puzzle([[1,1,2,2,2],[1,3,3,4,2],[1,3,5,4,4],[3,3,5,5,4],[5,5,5,4,4]]))"
```
