# 6장 영어 회화 연습 에이전트

마이크에 영어로 말하면 음성 인식(STT), 튜터 LLM, 음성 합성(TTS)을 차례로 거쳐 튜터가 소리로 대답하고, 틀린 표현은 화면에 교정해 주는 에이전트입니다. 연습을 마치면 학습 보고서를 출력합니다.

## 파일

| 파일 | 내용 | 책의 위치 |
|---|---|---|
| `english_tutor.py` | `record_audio`, `play_audio`, `transcribe`, `SYSTEM_PROMPT`, `get_tutor_response`, `speak`, `practice_session`, `generate_report` | 6장 '구현: 오디오 녹음과 재생'부터 '세션 보고서'까지 |

책과 다른 점은 다음과 같습니다.

- `english_tutor.py`: 마지막 실행 줄 `practice_session()`을 `if __name__ == "__main__":` 아래로 옮겼습니다. 다른 파일에서 이 파일을 import할 때 세션이 바로 시작되지 않게 하기 위해서입니다.
- 넣지 않은 코드: '지연 시간이라는 벽'의 스트리밍 호출은 `stream=True`의 동작을 보여 주는 설명용 조각이고 튜터 프로그램에는 들어가지 않아서 예제에서 뺐습니다.

## 실행

```bash
uv sync
echo "OPENAI_API_KEY=sk-..." > .env
uv run english_tutor.py    # 회화 연습 세션
```

마이크와 스피커가 필요합니다. 맥에서는 처음 실행할 때 터미널의 마이크 접근 권한을 허용해야 녹음이 됩니다. 녹음한 `input.wav`와 튜터 음성 `reply.wav`는 실행한 디렉터리에 만들어집니다.
