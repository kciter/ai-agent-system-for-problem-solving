"""calculator 모듈의 테스트(17장 '실행 결과' 절을 따라 해보기 위해 예제에서 만든 파일)."""
import pytest

from calculator import add, subtract, multiply, divide


def test_add():
    assert add(2, 3) == 5


def test_subtract():
    assert subtract(5, 3) == 2


def test_multiply():
    assert multiply(4, 3) == 12


def test_divide():
    assert divide(10, 2) == 5


def test_divide_by_zero():
    with pytest.raises(ValueError, match="0으로 나눌 수 없습니다"):
        divide(10, 0)
