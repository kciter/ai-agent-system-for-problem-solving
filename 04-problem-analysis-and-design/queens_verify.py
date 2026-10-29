"""4장 Queens 퍼즐 검증 코드(규칙 기반, LLM 없음).

책 4장 '검증 코드 구현'의 네 함수를 순서대로 옮겼습니다.
generator_v1.py와 generator_v2.py가 이 모듈의 verify_puzzle을 씁니다.
"""


def validate_solution(board, solution):
  """퀸 배치가 모든 규칙을 만족하는지 검증합니다.

  Args:
    board: 색상 영역을 나타내는 2차원 배열
    solution: 퀸의 위치 리스트 [(row, col), ...]

  Returns:
    (is_valid, errors) 튜플
  """
  n = len(board)
  errors = []

  # 퀸 개수 확인
  if len(solution) != n:
    errors.append(f"퀸이 {n}개여야 하지만 {len(solution)}개입니다.")
    return False, errors

  rows = [pos[0] for pos in solution]
  cols = [pos[1] for pos in solution]

  # 각 행에 정확히 하나의 퀸
  if len(set(rows)) != n:
    errors.append("같은 행에 두 개 이상의 퀸이 있습니다.")

  # 각 열에 정확히 하나의 퀸
  if len(set(cols)) != n:
    errors.append("같은 열에 두 개 이상의 퀸이 있습니다.")

  # 인접 금지 (상하좌우 + 대각선)
  for i in range(len(solution)):
    for j in range(i + 1, len(solution)):
      r1, c1 = solution[i]
      r2, c2 = solution[j]
      if abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1:
        errors.append(f"({r1},{c1})과 ({r2},{c2})가 인접합니다.")

  # 각 색상 영역에 정확히 하나의 퀸
  color_counts = {}
  for row, col in solution:
    color = board[row][col]
    color_counts[color] = color_counts.get(color, 0) + 1
  for color, count in color_counts.items():
    if count > 1:
      errors.append(f"색상 {color} 영역에 퀸이 {count}개입니다.")

  return len(errors) == 0, errors


def solve_queens(board):
  """퍼즐의 모든 정답을 찾습니다.

  백트래킹으로 가능한 모든 퀸 배치를 탐색합니다.
  정답이 2개 이상 발견되면 즉시 중단합니다.

  Returns:
    정답 리스트. 유일한 정답이면 길이 1, 여러 정답이면 길이 2.
  """
  n = len(board)
  solutions = []

  def is_safe(placed, row, col):
    for r, c in placed:
      # 같은 열
      if c == col:
        return False
      # 인접 (상하좌우 + 대각선)
      if abs(r - row) <= 1 and abs(c - col) <= 1:
        return False
      # 같은 색상 영역
      if board[r][c] == board[row][col]:
        return False
    return True

  def backtrack(row, placed):
    if len(solutions) >= 2:
      return  # 유일성 확인만 하면 되므로 2개 찾으면 중단
    if row == n:
      solutions.append(list(placed))
      return
    for col in range(n):
      if is_safe(placed, row, col):
        placed.append((row, col))
        backtrack(row + 1, placed)
        placed.pop()

  backtrack(0, [])
  return solutions


def are_regions_connected(board):
  """각 색상 영역이 상하좌우로 이어진 한 덩어리인지 확인합니다."""
  n = len(board)
  cells_by_color = {}
  for r in range(n):
    for c in range(n):
      cells_by_color.setdefault(board[r][c], []).append((r, c))

  for color, cells in cells_by_color.items():
    # 영역의 첫 칸에서 시작해 같은 색 칸만 따라 탐색
    visited = {cells[0]}
    queue = [cells[0]]
    while queue:
      r, c = queue.pop(0)
      for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
        if (0 <= nr < n and 0 <= nc < n
            and board[nr][nc] == color and (nr, nc) not in visited):
          visited.add((nr, nc))
          queue.append((nr, nc))
    if len(visited) != len(cells):
      return False  # 방문하지 못한 칸이 있으면 조각난 영역
  return True


def verify_puzzle(board):
  """퍼즐이 유효한지 종합 검증합니다.

  Returns:
    {"valid": bool, "unique": bool, "solution": list | None, "errors": list}
  """
  n = len(board)
  errors = []

  # 기본 구조 검증
  if not all(len(row) == n for row in board):
    return {"valid": False, "unique": False, "solution": None,
            "errors": ["격자가 정사각형이 아닙니다."]}

  # 색상 영역 개수 확인
  colors = set()
  for row in board:
    for cell in row:
      colors.add(cell)
  if len(colors) != n:
    errors.append(f"색상 영역이 {n}개여야 하지만 {len(colors)}개입니다.")

  # 색상 영역 연결성 확인
  if not are_regions_connected(board):
    errors.append("조각나서 이어지지 않은 색상 영역이 있습니다.")

  if errors:
    return {"valid": False, "unique": False, "solution": None,
            "errors": errors}

  # 정답 찾기
  solutions = solve_queens(board)

  if len(solutions) == 0:
    return {"valid": False, "unique": False, "solution": None,
            "errors": ["풀이 가능한 정답이 없습니다."]}
  if len(solutions) >= 2:
    return {"valid": False, "unique": False, "solution": solutions[0],
            "errors": [f"정답이 유일하지 않습니다. {solutions[0]}와 "
                       f"{solutions[1]} 모두 정답입니다."]}

  # 정답 검증
  is_valid, validation_errors = validate_solution(board, solutions[0])
  return {"valid": is_valid, "unique": True, "solution": solutions[0],
          "errors": validation_errors}
