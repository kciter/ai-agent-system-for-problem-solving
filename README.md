# 문제 해결을 위한 AI 에이전트 설계 예제 코드

『문제 해결을 위한 AI 에이전트 설계』(이선협 지음, 한빛미디어, 2026)의 예제 코드입니다. 책에 나오는 코드를 장별로 모아, 그대로 실행해 볼 수 있게 정리했습니다.

## 장별 디렉터리

| 디렉터리 | 장 | 대표 실행 |
|---|---|---|
| [`03-building-a-simple-agent`](03-building-a-simple-agent) | 3장 간단한 AI 에이전트 만들어보기 | `uv run step4_function_calling.py` |
| [`04-problem-analysis-and-design`](04-problem-analysis-and-design) | 4장 문제 이해와 설계 결정 | `uv run generator_v2.py` |
| [`05-text-adventure-game`](05-text-adventure-game) | 5장 텍스트 어드벤처 게임 | `uv run game.py` |
| [`06-english-tutor-agent`](06-english-tutor-agent) | 6장 영어 회화 연습 에이전트 | `uv run english_tutor.py` |
| [`07-research-agent`](07-research-agent) | 7장 자동 리서치 에이전트 | `uv run research_agent.py` |
| [`08-reliability`](08-reliability) | 8장 신뢰성 있는 에이전트 만들기 | `uv run research_agent.py` |
| [`09-cost-and-security`](09-cost-and-security) | 9장 비용과 보안 | `uv run research_agent.py`, `uv run cost.py` |
| [`10-agent-evaluation`](10-agent-evaluation) | 10장 에이전트 평가 | `uv run evaluation.py` |
| [`11-context-and-memory`](11-context-and-memory) | 11장 컨텍스트와 메모리 | `uv run memory.py` |
| [`12-multi-agent-systems`](12-multi-agent-systems) | 12장 멀티 에이전트 시스템 | `uv run research_team.py` |
| [`13-plugin-architecture`](13-plugin-architecture) | 13장 플러그인 아키텍처 | `uv run main.py` |
| [`14-mcp`](14-mcp) | 14장 도구 연결의 표준 MCP | `uv run main.py` |
| [`15-frameworks`](15-frameworks) | 15장 에이전트 프레임워크 | `uv run step2_research_graph.py` |
| [`16-coding-agent`](16-coding-agent) | 16장 코딩 에이전트 만들기 | `uv run main.py` |

장마다 README에 파일 목록, 책의 어느 부분인지, 책과 다른 점, 실행 방법을 적어 두었습니다. 각 디렉터리는 앞 장의 코드가 필요하면 그것까지 담고 있어서 따로 실행할 수 있습니다.

1장과 2장은 개념을 설명하는 짧은 코드 조각만 있어서 디렉터리가 없습니다. 다른 장에서도 실행하는 프로그램이 아니라 설명을 위해 넣은 조각은 예제에 넣지 않았습니다.

## 준비

파이썬 3.10 이상과 오픈AI API 키가 필요합니다. API는 사용한 만큼 비용이 청구됩니다.

예제는 [uv](https://docs.astral.sh/uv/)로 관리합니다. uv는 파이썬과 가상 환경, 패키지를 함께 관리하는 도구입니다. 파이썬이 설치되어 있지 않아도 uv가 필요한 버전을 받아서 씁니다.

```bash
# 맥, 리눅스
curl -LsSf https://astral.sh/uv/install.sh | sh
# 윈도우(PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

장마다 `pyproject.toml`과 `uv.lock`이 있는 독립된 프로젝트입니다. 실행하려는 장의 디렉터리에서 `uv sync`로 패키지를 설치하고 `uv run`으로 실행합니다.

```bash
git clone https://github.com/kciter/ai-agent-system-for-problem-solving.git
cd ai-agent-system-for-problem-solving
echo "OPENAI_API_KEY=sk-..." > .env   # API 키

cd 07-research-agent
uv sync                                # .venv를 만들고 uv.lock의 버전대로 설치
uv run research_agent.py
```

예제는 3장처럼 `load_dotenv()`로 `.env`의 API 키를 읽습니다. `.env`는 실행하는 파일의 디렉터리부터 위로 올라가며 찾으므로, 저장소 최상위에 하나만 두면 모든 장이 함께 씁니다. `.env`는 `.gitignore`에 들어 있어 커밋되지 않습니다.

`uv.lock`에는 확인한 버전이 고정되어 있어서, 나중에 설치해도 같은 버전이 설치됩니다. 지금 고정한 주요 버전은 openai 3.35.1, python-dotenv 1.2.4, ddgs 9.16.0, trafilatura 2.3.1, sounddevice 0.5.6, soundfile 0.14.0, mcp 2.3.0, langchain 1.4.6, langchain-openai 1.7.2, langgraph 1.2.16입니다. 파이썬은 설치된 것 가운데 3.10 이상인 가장 새 버전을 씁니다. 특정 버전을 쓰려면 `uv sync --python 3.11`처럼 지정합니다.

### uv 없이 실행하기

책은 `pip install`로 라이브러리를 설치하도록 안내합니다. uv를 쓰지 않으려면 가상 환경을 만든 뒤, 각 장 `pyproject.toml`의 `dependencies`에 적힌 패키지를 `pip install`로 설치하고 `python research_agent.py`처럼 실행하면 됩니다.

```bash
cd 07-research-agent
python3 -m venv .venv
source .venv/bin/activate              # 윈도우: .venv\Scripts\activate
pip install openai python-dotenv ddgs trafilatura
python research_agent.py
```

## 책과 다른 점

코드는 책의 코드를 그대로 옮겼습니다. 실행하려면 필요하지만 책에는 본문으로만 설명한 줄(import, `load_dotenv()`, 실행 진입점 등)을 덧붙인 곳에는 `# [예제 보충]` 주석을 달았습니다. 각 장 README의 "책과 다른 점"에 무엇을 왜 바꿨는지 정리했습니다.

책에 나오는 모델 이름과 가격은 집필 시점 기준입니다. 새 모델로 바꿔 실행할 때 확인할 점은 책 3장 '사용할 모델'에 정리되어 있습니다.

## 문의

코드가 실행되지 않거나 책의 내용과 다른 점을 발견하면 [Issues](https://github.com/kciter/ai-agent-system-for-problem-solving/issues)에 남겨 주세요. 라이브러리가 바뀌어 코드를 고쳐야 할 때도 이 저장소에 먼저 반영합니다.
