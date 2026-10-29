# 5장 텍스트 어드벤처 게임: 무인도에서 살아남기

LLM이 게임 마스터로 이야기를 만들고, 상태(체력·허기·갈증·인벤토리·날짜)는 코드가 규칙대로 관리하는 텍스트 어드벤처 게임입니다. 확률 판정은 주사위 도구가 맡습니다.

## 파일

| 파일 | 내용 | 책의 위치 |
|---|---|---|
| `game.py` | `initial_state`, `SYSTEM_PROMPT`, `parse_response`, `apply_state_changes`, `display_status`, `roll_dice`와 도구 정의, `handle_tool_calls`, `play_game` | 5장 '게임 설계'부터 '구현: 게임 루프'까지 |
| `game_with_summary.py` | `game.py`에 `summarize_history`를 더하고 메인 루프에서 호출하도록 연결한 판 | '세계관 일관성 유지' |

## 책과 다른 점

- 게임 루프 블록의 마지막 줄 `play_game()`을 `if __name__ == "__main__":` 아래로 옮겼습니다. 다른 파일에서 import할 때 게임이 바로 시작되지 않게 하기 위해서입니다.
- 요약 기능은 책에서 "추가로 적용할 수 있다"는 개선이라 별도 파일 `game_with_summary.py`로 두었습니다. `game.py`와 같은 코드에 `summarize_history`를 `play_game` 앞에 넣고, 책의 연결 코드(`if len(messages) > 20: ...`)를 메인 루프에 넣었습니다. 책은 "메인 루프에서 사용자 입력을 받은 직후"라고만 해서, 종료 명령 확인 바로 다음(현재 상태를 담은 user 메시지를 만들기 전)에 두었습니다(`# [예제 보충]` 표시).
- 책의 5장 코드에는 `load_dotenv()`가 없습니다. 그대로 두면 `.env`에 둔 API 키를 읽지 못해 시작하자마자 오류가 나므로, 3장과 같은 방식으로 `load_dotenv()`를 넣었습니다(`# [예제 보충]` 표시).
- 그 밖에는 책의 코드를 순서 그대로 이어 붙였습니다.

## 실행

```bash
uv sync
echo "OPENAI_API_KEY=sk-..." > .env
uv run game.py                # 기본 게임
uv run game_with_summary.py   # 대화 히스토리 요약을 더한 게임
```

행동을 입력해 진행하고, `quit` 또는 `종료`로 끝냅니다.
