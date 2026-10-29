"""3장 '도구 정의하기'의 tools.py. 날씨(임의의 값)와 현재 시각을 돌려주는 도구 함수."""

import random
from datetime import datetime

def get_current_weather(location: str) -> str:
  """지정된 위치의 현재 날씨를 반환합니다.

  Args:
    location: 도시 이름 (예: "서울", "부산")

  Returns:
    날씨 정보 문자열
  """
  # 실제로는 날씨 API를 호출해야 하지만, 여기서는 임의의 값을 반환
  weather_conditions = ["맑음", "흐림", "비", "눈"]
  temperature = random.randint(0, 35)
  condition = random.choice(weather_conditions)

  return f"{location}의 현재 날씨: {condition}, 기온: {temperature}도"

def get_current_time() -> str:
  """현재 시각을 반환합니다."""
  return datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")
