import pygame
import sys
import random
import heapq
import math
from collections import deque

# Khởi tạo Pygame
pygame.init()
pygame.font.init()

# Cấu hình màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (40, 40, 40)
LIGHT_BLACK = (20, 20, 20)
RED = (231, 76, 60)
GREEN = (46, 204, 113)
BLUE = (52, 152, 219)
YELLOW = (241, 196, 15)
ORANGE = (230, 126, 34)
PURPLE = (155, 89, 182)
PINK = (254, 130, 153)
CYAN = (0, 220, 220)

SCREEN_WIDTH = 1350
SCREEN_HEIGHT = 780
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Vacuum Agent Simulator - Full Advanced Integration with HCMC CSP")

# ==============================================================================
# SỬA LỖI FONT CHỮ: Chuyển sang Segoe UI hoặc sans để hỗ trợ đầy đủ tiếng Việt unicode
# ==============================================================================
def _load_font(size, bold=False):
    """Thử các font hỗ trợ tiếng Việt, fallback an toàn."""
    for name in ["Segoe UI", "Arial Unicode MS", "DejaVu Sans", "FreeSans"]:
        f = pygame.font.SysFont(name, size, bold=bold)
        if f.get_height() > 0:
            return f
    return pygame.font.Font(None, size)

font       = _load_font(14)
font_small = _load_font(12)
font_bold  = _load_font(16, bold=True)

# ==============================================================================
# DỮ LIỆU CSP BẢN ĐỒ CÁC QUẬN TP.HCM
# ==============================================================================
MAP_COLORS = {
    "Đỏ": (231, 76, 60),
    "Xanh lá": (46, 204, 113),
    "Xanh dương": (52, 152, 219),
    "Vàng": (241, 196, 15)
}
COLOR_NAMES = list(MAP_COLORS.keys())

QUAN_DATA = {
    "Quận 1":    {"adj": ["Quận 3", "Quận 4", "Quận 5", "Bình Thạnh", "Phú Nhuận"], "pos": (350, 360), "w": 90, "h": 65},
    "Quận 3":    {"adj": ["Quận 1", "Quận 10", "Phú Nhuận", "Tân Bình"], "pos": (230, 300), "w": 90, "h": 65},
    "Quận 4":    {"adj": ["Quận 1", "Quận 7"], "pos": (460, 430), "w": 85, "h": 55},
    "Quận 5":    {"adj": ["Quận 1", "Quận 10", "Quận 11", "Quận 6", "Quận 8"], "pos": (230, 430), "w": 90, "h": 65},
    "Quận 6":    {"adj": ["Quận 5", "Quận 11", "Quận 8", "Bình Tân"], "pos": (110, 480), "w": 90, "h": 65},
    "Quận 7":    {"adj": ["Quận 4", "Quận 8"], "pos": (460, 520), "w": 100, "h": 75},
    "Quận 8":    {"adj": ["Quận 5", "Quận 6", "Quận 7", "Bình Tân"], "pos": (230, 530), "w": 110, "h": 65},
    "Quận 10":   {"adj": ["Quận 3", "Quận 5", "Quận 11", "Tân Bình"], "pos": (230, 190), "w": 90, "h": 65},
    "Quận 11":   {"adj": ["Quận 10", "Quận 5", "Quận 6", "Tân Bình", "Tân Phú"], "pos": (110, 300), "w": 90, "h": 65},
    "Bình Thạnh": {"adj": ["Quận 1", "Phú Nhuận", "Gò Vấp"], "pos": (460, 260), "w": 100, "h": 75},
    "Phú Nhuận": {"adj": ["Quận 1", "Quận 3", "Bình Thạnh", "Gò Vấp", "Tân Bình"], "pos": (350, 220), "w": 90, "h": 65},
    "Gò Vấp":    {"adj": ["Bình Thạnh", "Phú Nhuận", "Tân Bình"], "pos": (440, 100), "w": 100, "h": 75},
    "Tân Bình":  {"adj": ["Quận 3", "Quận 10", "Quận 11", "Phú Nhuận", "Gò Vấp", "Tân Phú"], "pos": (320, 100), "w": 90, "h": 75},
    "Tân Phú":   {"adj": ["Tân Bình", "Quận 11", "Bình Tân"], "pos": (110, 100), "w": 90, "h": 75},
    "Bình Tân":  {"adj": ["Tân Phú", "Quận 6", "Quận 8"], "pos": (110, 590), "w": 90, "h": 75}
}
CSP_VARIABLES = list(QUAN_DATA.keys())

# Gioi han vong lap thuat toan
IDA_STAR_MAX_LOOPS   = 30000
BEAM_SEARCH_MAX_ITER = 300

class CSPState:
    def __init__(self):
        self.assignment = {}
        self.domains = {v: COLOR_NAMES.copy() for v in CSP_VARIABLES}
        self.history = []
        self.current_variable = None
        self.logs = ["Khởi tạo CSP Tô màu bản đồ TP.HCM...", "Phân hoạch = {}"]
        self.done = False

    def is_consistent(self, var, color):
        for neighbor in QUAN_DATA[var]["adj"]:
            if neighbor in self.assignment and self.assignment[neighbor] == color:
                return False
        return True

    def step(self):
        if len(self.assignment) == len(CSP_VARIABLES):
            if not self.done:
                self.logs.append("Thành công! Toàn bộ bản đồ đã được tô màu hợp lệ.")
                self.done = True
            return True

        unassigned = [v for v in CSP_VARIABLES if v not in self.assignment]
        if not unassigned: return True
        
        var = unassigned[0]
        self.current_variable = var
        available_colors = [c for c in self.domains[var]]
        
        if not available_colors:
            self.logs.append(f"Xung đột tại {var}: Không còn màu hợp lệ trong miền giá trị!")
            if self.history:
                last_var, last_color, saved_domains = self.history.pop()
                if last_var in self.assignment:
                    del self.assignment[last_var]
                self.domains = saved_domains
                if last_color in self.domains[last_var]:
                    self.domains[last_var].remove(last_color)
                self.logs.append(f"-> Quay lui (Backtrack): Hủy {last_var}, thử màu khác.")
            else:
                self.logs.append("Thất bại: Bài toán không thể tìm ra lời giải!")
                self.done = True
            return False

        color = available_colors[0]
        saved_domains = {v: self.domains[v].copy() for v in CSP_VARIABLES}
        
        self.logs.append(f"Chọn biến tiếp theo: {var}")
        self.logs.append(f"-> Thử gán giá trị: {var} = {color}")
        
        if self.is_consistent(var, color):
            self.assignment[var] = color
            self.logs.append(f"   Kiểm tra ràng buộc: Hợp lệ!")
            self.history.append((var, color, saved_domains))
            
            self.logs.append(f"   [Kiểm tra trước] Cập nhật miền giá trị các vùng kề của {var}:")
            for neighbor in QUAN_DATA[var]["adj"]:
                if neighbor not in self.assignment and color in self.domains[neighbor]:
                    self.domains[neighbor].remove(color)
                    self.logs.append(f"     + Miền giá trị của {neighbor} loại bớt màu {color} -> {self.domains[neighbor]}")
            self.logs.append(f"   Phân hoạch hiện tại = {self.assignment}")
        else:
            self.logs.append(f"   Kiểm tra ràng buộc: Vi phạm trùng màu kề -> Không hợp lệ!")
            self.domains[var].remove(color)
        return False

# ==============================================================================
# 8-QUEENS CSP – BA BIẾN THỂ BACKTRACKING
# ==============================================================================
N_QUEENS = 8  # Kích thước bàn cờ

class QueensCSP:
    """
    Mô phỏng từng bước giải bài toán 8-Queens với 3 chiến lược:
      - 'simple'  : Simple Backtracking (chọn cột theo thứ tự, thử giá trị theo thứ tự)
      - 'mrv'     : Backtracking + MRV  (chọn cột có ít giá trị hợp lệ nhất)
      - 'fc'      : Backtracking + Forward Checking (loại trừ miền trước khi đặt quân)
    """
    def __init__(self, strategy='simple'):
        self.strategy = strategy
        self.n = N_QUEENS
        # assignment[col] = row  (None = chưa gán)
        self.assignment = {}
        # domains[col] = tập hàng còn hợp lệ
        self.domains = {c: list(range(self.n)) for c in range(self.n)}
        self.history = []          # stack để backtrack: (col, row, domains_snapshot)
        self.logs = []
        self.done = False
        self.success = False
        self.nodes_explored = 0
        self.backtracks = 0
        self._add_log(f"Khởi tạo 8-Queens CSP [{strategy.upper()}]")
        self._add_log(f"Biến: 8 cột (0-7) | Miền: hàng 0-7 | Ràng buộc: không tấn công nhau")

    def _add_log(self, msg):
        self.logs.append(msg)
        if len(self.logs) > 200:
            self.logs = self.logs[-200:]

    def _is_consistent(self, col, row):
        """Kiểm tra quân hậu tại (row, col) có xung đột với các quân đã đặt."""
        for c, r in self.assignment.items():
            if r == row:                        return False  # cùng hàng
            if abs(c - col) == abs(r - row):    return False  # chéo
        return True

    def _select_unassigned(self):
        """Chọn biến tiếp theo theo chiến lược."""
        unassigned = [c for c in range(self.n) if c not in self.assignment]
        if not unassigned:
            return None
        if self.strategy == 'mrv':
            # MRV: chọn biến có ít giá trị hợp lệ nhất
            def count_valid(col):
                return sum(1 for r in self.domains[col] if self._is_consistent(col, r))
            col = min(unassigned, key=count_valid)
            valid_counts = {c: sum(1 for r in self.domains[c] if self._is_consistent(c, r)) for c in unassigned}
            self._add_log(f"  MRV – số giá trị hợp lệ: { {c: valid_counts[c] for c in unassigned} }")
            return col
        else:
            return unassigned[0]  # simple / fc: chọn cột nhỏ nhất

    def _forward_check(self, col, row):
        """
        Forward Checking: loại giá trị xung đột khỏi miền các cột chưa gán.
        Trả về dict {other_col: [removed_rows]} hoặc None nếu có miền rỗng.
        """
        pruned = {}
        for other_col in range(self.n):
            if other_col in self.assignment or other_col == col:
                continue
            removed = []
            new_domain = []
            for r in self.domains[other_col]:
                if r == row or abs(other_col - col) == abs(r - row):
                    removed.append(r)
                else:
                    new_domain.append(r)
            if removed:
                self.domains[other_col] = new_domain
                pruned[other_col] = removed
                if not new_domain:
                    # Miền rỗng → thất bại sớm
                    self._add_log(f"  FC: Miền cột {other_col} rỗng sau khi đặt Q{col}=hàng{row} → Backtrack sớm!")
                    return None
        return pruned

    def step(self):
        """Thực hiện MỘT bước: thử gán hoặc backtrack. Trả về True khi xong."""
        if self.done:
            return True

        self.nodes_explored += 1

        # --- Chọn biến ---
        col = self._select_unassigned()
        if col is None:
            # Tất cả đã gán → thành công
            self._add_log(f"✔ Thành công! Lời giải: { {c: self.assignment[c] for c in range(self.n)} }")
            self.done = True
            self.success = True
            return True

        self._add_log(f"Bước {self.nodes_explored}: Chọn cột {col} | Miền còn: {self.domains[col]}")

        # Tìm giá trị hợp lệ đầu tiên trong domain
        chosen_row = None
        tried = []
        for r in list(self.domains[col]):
            if self._is_consistent(col, r):
                chosen_row = r
                break
            tried.append(r)

        if chosen_row is None:
            # Không có giá trị nào hợp lệ → Backtrack
            self.backtracks += 1
            self._add_log(f"  Cột {col}: Hết giá trị hợp lệ → Backtrack! (lần thứ {self.backtracks})")
            if not self.history:
                self._add_log("✘ Thất bại: Không tìm được lời giải!")
                self.done = True
                return True
            prev_col, prev_row, domain_snapshot, pruned_snapshot = self.history.pop()
            del self.assignment[prev_col]
            # Khôi phục domains
            self.domains = {c: list(v) for c, v in domain_snapshot.items()}
            # Loại prev_row khỏi domain của prev_col để không thử lại
            if prev_row in self.domains[prev_col]:
                self.domains[prev_col].remove(prev_row)
            self._add_log(f"  Quay lui tới cột {prev_col}, bỏ hàng {prev_row}, thử tiếp domain: {self.domains[prev_col]}")
            return False

        # Gán giá trị
        domain_snapshot = {c: list(v) for c, v in self.domains.items()}
        pruned_snapshot = {}

        self._add_log(f"  Thử Q{col} = hàng {chosen_row} ✓")

        if self.strategy == 'fc':
            pruned_snapshot = self._forward_check(col, chosen_row)
            if pruned_snapshot is None:
                # FC phát hiện miền rỗng → backtrack ngay
                self.backtracks += 1
                self.domains = {c: list(v) for c, v in domain_snapshot.items()}
                if self.domains[col]:
                    self.domains[col].remove(chosen_row)
                self._add_log(f"  FC Backtrack ngay tại cột {col}! (lần thứ {self.backtracks})")
                return False
            if pruned_snapshot:
                for oc, removed in pruned_snapshot.items():
                    self._add_log(f"  FC: Cột {oc} loại bỏ hàng {removed} → còn {self.domains[oc]}")

        self.assignment[col] = chosen_row
        self.history.append((col, chosen_row, domain_snapshot, pruned_snapshot))
        self._add_log(f"  Gán Q{col}=hàng{chosen_row} | Đã gán: {len(self.assignment)}/8 cột")
        return False

# ==============================================================================
# TIC-TAC-TOE (CỜ CARO 3x3) – BÀI TOÁN GAME ĐỐI KHÁNG
# Minimax / Alpha-Beta Pruning / Expectimax
# ==============================================================================
TTT_HUMAN = 'X'   # Người chơi đi trước
TTT_AI = 'O'      # AI (MAX trong minimax)

class TicTacToeGame:
    """
    Mô phỏng game Tic-Tac-Toe với AI dùng 1 trong 3 thuật toán:
      - 'minimax'   : Minimax thuần (đối thủ chơi tối ưu, MIN)
      - 'alphabeta' : Minimax + cắt tỉa Alpha-Beta (đếm số nhánh bị cắt)
      - 'expectimax': Đối thủ đánh NGẪU NHIÊN (nút Chance thay vì MIN)
    """
    def __init__(self, strategy='minimax'):
        self.strategy = strategy
        self.board = [' '] * 9   # 0..8, hàng-major
        self.turn = TTT_HUMAN    # Người đi trước (X)
        self.winner = None       # 'X' / 'O' / 'draw' / None
        self.logs = []
        self.nodes_explored = 0
        self.pruned_branches = 0   # chỉ dùng cho alpha-beta
        self.last_eval = None      # giá trị minimax của nước đi cuối AI chọn
        self.game_over = False
        self.ai_thinking_done = True   # True = đã xử lý xong lượt hiện tại
        self._add_log(f"Khởi tạo Tic-Tac-Toe [{strategy.upper()}] – Bạn (X) đi trước, AI (O) dùng {strategy}")

    def _add_log(self, msg):
        self.logs.append(msg)
        if len(self.logs) > 150:
            self.logs = self.logs[-150:]

    # ---------- Logic game cơ bản ----------
    WIN_LINES = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]

    def _check_winner(self, board):
        for a,b,c in self.WIN_LINES:
            if board[a] != ' ' and board[a] == board[b] == board[c]:
                return board[a]
        if ' ' not in board:
            return 'draw'
        return None

    def _available_moves(self, board):
        return [i for i in range(9) if board[i] == ' ']

    def human_move(self, idx):
        """Người chơi click vào ô idx."""
        if self.game_over or self.turn != TTT_HUMAN or self.board[idx] != ' ':
            return False
        self.board[idx] = TTT_HUMAN
        self._add_log(f"Bạn (X) đánh vào ô {idx}")
        result = self._check_winner(self.board)
        if result:
            self._finish(result)
        else:
            self.turn = TTT_AI
            self.ai_thinking_done = False
        return True

    def _finish(self, result):
        self.winner = result
        self.game_over = True
        if result == 'draw':
            self._add_log("Kết quả: HÒA!")
        else:
            self._add_log(f"Kết quả: {result} THẮNG!")

    # ---------- MINIMAX THUẦN ----------
    def _minimax(self, board, is_maximizing, depth):
        self.nodes_explored += 1
        result = self._check_winner(board)
        if result == TTT_AI:   return 10 - depth
        if result == TTT_HUMAN: return depth - 10
        if result == 'draw':   return 0

        if is_maximizing:
            best = -math.inf
            for m in self._available_moves(board):
                board[m] = TTT_AI
                val = self._minimax(board, False, depth + 1)
                board[m] = ' '
                best = max(best, val)
            return best
        else:
            best = math.inf
            for m in self._available_moves(board):
                board[m] = TTT_HUMAN
                val = self._minimax(board, True, depth + 1)
                board[m] = ' '
                best = min(best, val)
            return best

    def _best_move_minimax(self):
        best_val, best_move = -math.inf, None
        for m in self._available_moves(self.board):
            self.board[m] = TTT_AI
            val = self._minimax(self.board, False, 1)
            self.board[m] = ' '
            self._add_log(f"  Thử ô {m}: minimax value = {val}")
            if val > best_val:
                best_val, best_move = val, m
        return best_move, best_val

    # ---------- ALPHA-BETA PRUNING ----------
    def _alphabeta(self, board, is_maximizing, depth, alpha, beta):
        self.nodes_explored += 1
        result = self._check_winner(board)
        if result == TTT_AI:   return 10 - depth
        if result == TTT_HUMAN: return depth - 10
        if result == 'draw':   return 0

        if is_maximizing:
            best = -math.inf
            for m in self._available_moves(board):
                board[m] = TTT_AI
                val = self._alphabeta(board, False, depth + 1, alpha, beta)
                board[m] = ' '
                best = max(best, val)
                alpha = max(alpha, best)
                if beta <= alpha:
                    self.pruned_branches += 1
                    break  # cắt tỉa nhánh beta
            return best
        else:
            best = math.inf
            for m in self._available_moves(board):
                board[m] = TTT_HUMAN
                val = self._alphabeta(board, True, depth + 1, alpha, beta)
                board[m] = ' '
                best = min(best, val)
                beta = min(beta, best)
                if beta <= alpha:
                    self.pruned_branches += 1
                    break  # cắt tỉa nhánh alpha
            return best

    def _best_move_alphabeta(self):
        best_val, best_move = -math.inf, None
        alpha, beta = -math.inf, math.inf
        for m in self._available_moves(self.board):
            self.board[m] = TTT_AI
            val = self._alphabeta(self.board, False, 1, alpha, beta)
            self.board[m] = ' '
            self._add_log(f"  Thử ô {m}: alpha-beta value = {val} (alpha={alpha}, beta={beta})")
            if val > best_val:
                best_val, best_move = val, m
            alpha = max(alpha, best_val)
        return best_move, best_val

    # ---------- EXPECTIMAX (đối thủ ngẫu nhiên) ----------
    def _expectimax(self, board, is_maximizing, depth):
        self.nodes_explored += 1
        result = self._check_winner(board)
        if result == TTT_AI:   return 10 - depth
        if result == TTT_HUMAN: return depth - 10
        if result == 'draw':   return 0

        moves = self._available_moves(board)
        if is_maximizing:
            best = -math.inf
            for m in moves:
                board[m] = TTT_AI
                val = self._expectimax(board, False, depth + 1)
                board[m] = ' '
                best = max(best, val)
            return best
        else:
            # Nút CHANCE: đối thủ đánh ngẫu nhiên đều giữa các ô trống
            total = 0
            for m in moves:
                board[m] = TTT_HUMAN
                val = self._expectimax(board, True, depth + 1)
                board[m] = ' '
                total += val
            return total / len(moves) if moves else 0

    def _best_move_expectimax(self):
        best_val, best_move = -math.inf, None
        for m in self._available_moves(self.board):
            self.board[m] = TTT_AI
            val = self._expectimax(self.board, False, 1)
            self.board[m] = ' '
            self._add_log(f"  Thử ô {m}: expected value = {val:.2f}")
            if val > best_val:
                best_val, best_move = val, m
        return best_move, best_val

    def ai_move(self):
        """AI tính và thực hiện nước đi (gọi 1 lần mỗi lượt AI)."""
        if self.game_over or self.turn != TTT_AI or self.ai_thinking_done:
            return
        self.nodes_explored = 0
        self.pruned_branches = 0
        self._add_log(f"--- AI ({self.strategy.upper()}) đang suy nghĩ ---")

        if self.strategy == 'minimax':
            move, val = self._best_move_minimax()
        elif self.strategy == 'alphabeta':
            move, val = self._best_move_alphabeta()
        else:  # expectimax
            move, val = self._best_move_expectimax()

        self.last_eval = val
        if move is not None:
            self.board[move] = TTT_AI
            self._add_log(f"=> AI chọn ô {move} (giá trị={val:.2f}, nodes={self.nodes_explored}" +
                           (f", pruned={self.pruned_branches}" if self.strategy == 'alphabeta' else "") + ")")
            result = self._check_winner(self.board)
            if result:
                self._finish(result)
            else:
                self.turn = TTT_HUMAN
        self.ai_thinking_done = True

    def reset(self):
        self.board = [' '] * 9
        self.turn = TTT_HUMAN
        self.winner = None
        self.game_over = False
        self.nodes_explored = 0
        self.pruned_branches = 0
        self.last_eval = None
        self.ai_thinking_done = True
        self.logs = []
        self._add_log(f"Reset ván mới [{self.strategy.upper()}] – Bạn (X) đi trước")

# ==============================================================================
# HÀM HEURISTIC CHUẨN HOÁ
# ==============================================================================
def calc_heuristic(state):
    if isinstance(state, frozenset):
        return len(state)
    pos, dirts = state
    if not dirts:
        return 0
    min_dist = min(abs(pos[0] - d[0]) + abs(pos[1] - d[1]) for d in dirts)
    h_val = min_dist + len(dirts)
    if pos in dirts:
        h_val -= 1  # FIX: giu h(n)>=0
    return max(0, h_val)  # FIX: clamp tranh am

# ==============================================================================
# LỚP NODE ĐỒNG BỘ CẤU TRÚC
# ==============================================================================
class Node:
    def __init__(self, state, parent=None, action=None, path_cost=0, depth=0, algo_type='bfs'):
        self.state = state  
        self.parent = parent
        self.action = action
        self.path_cost = path_cost  
        self.depth = depth          
        self.algo_type = algo_type  
        
        if algo_type in ['astar', 'idastar']:
            self.f_eval = path_cost + calc_heuristic(state)
        elif algo_type in ['greedy', 'shill', 'sthill', 'stochill', 'rrhill', 'beams', 'anneal']:
            self.f_eval = calc_heuristic(state)
        else:
            self.f_eval = path_cost

    def __lt__(self, other):
        return self.f_eval < other.f_eval

    def __repr__(self):
        if self.algo_type in ['blind1', 'blind2', 'blind3']:
            return f"BeliefNode(possible_positions={list(self.state)}, action='{self.action}', depth={self.depth})"
        if self.algo_type == 'and_or':
            return f"AndOrNode(state_pos={self.state[0]}, dirts_count={len(self.state[1])}, last_action='{self.action}')"
            
        parent_pos = self.parent.state[0] if self.parent else None
        if self.algo_type == 'ucs':
            return f"Node(state={self.state[0]}, parent={parent_pos}, cost_g={self.path_cost}, action='{self.action}')"
        elif self.algo_type in ['greedy', 'shill', 'sthill', 'stochill', 'rrhill', 'beams', 'anneal']:
            h_val = calc_heuristic(self.state)
            return f"Node(state={self.state[0]}, parent={parent_pos}, cost_h={h_val}, action='{self.action}')"
        elif self.algo_type in ['astar', 'idastar']:
            return f"Node(state={self.state[0]}, parent={parent_pos}, cost_f={self.f_eval}, action='{self.action}')"
        else:
            return f"Node(state={self.state[0]}, parent={parent_pos}, depth={self.depth}, action='{self.action}')"

class Environment:
    def __init__(self, size=4, num_dirt=3):
        self.size = size
        self.num_dirt = num_dirt
        self.agent_pos = (0, 0)
        self.obstacles = set()
        self.dirt_positions = set()
        self.blind1_target_goal = None  # FIX: co dinh target
        self.generate_map()

    def generate_map(self):
        self.agent_pos = (0, 0)
        self.obstacles = set()
        self.dirt_positions = set()
        for i in range(self.size):
            for j in range(self.size):
                if (i, j) != (0, 0) and random.random() < 0.15:
                    self.obstacles.add((i, j))
        all_cells = [(i, j) for i in range(self.size) for j in range(self.size) 
                     if (i, j) != (0, 0) and (i, j) not in self.obstacles]
        chosen_dirts = random.sample(all_cells, min(self.num_dirt, len(all_cells)))
        self.dirt_positions = set(chosen_dirts)
        # FIX: Co dinh blind1 target moi khi generate map
        preferred = (self.size - 1, self.size - 1)
        if preferred not in self.obstacles:
            self.blind1_target_goal = preferred
        else:
            free = [(i,j) for i in range(self.size) for j in range(self.size) if (i,j) not in self.obstacles]
            self.blind1_target_goal = random.choice(free) if free else (0,0)

    def get_initial_state(self):
        return (self.agent_pos, frozenset(self.dirt_positions))

    def is_goal(self, state):
        return len(state[1]) == 0

    def get_actions(self, state=None):
        if isinstance(state, frozenset) or state is None:
            return ['up', 'down', 'left', 'right']
        actions = []
        pos, dirts = state
        x, y = pos
        if pos in dirts:
            actions.append('suck')
        moves = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}
        for move, (dx, dy) in moves.items():
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size and (nx, ny) not in self.obstacles:
                actions.append(move)
        return actions

    def result(self, state, action):
        pos, dirts = state
        x, y = pos
        if action == 'suck':
            new_dirts = frozenset(dirts - {pos})
            return (pos, new_dirts)
        else:
            moves = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}
            dx, dy = moves[action]
            return ((x + dx, y + dy), dirts)

    def transition_belief(self, belief_state, action):
        next_belief = set()
        moves = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}
        dx, dy = moves[action]
        for (x, y) in belief_state:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size and (nx, ny) not in self.obstacles:
                next_belief.add((nx, ny))
            else:
                next_belief.add((x, y))
        return frozenset(next_belief)

    def is_goal_belief(self, belief_state, case_type):
        if case_type == 'blind1':
            # FIX: Dung target co dinh thay vi random moi lan
            return len(belief_state) == 1 and self.blind1_target_goal in belief_state
        elif case_type == 'blind2':
            if not self.dirt_positions: return False
            return belief_state.issubset(self.dirt_positions)
        elif case_type == 'blind3':
            target_column = self.size - 1
            goal_region = {(i, target_column) for i in range(self.size) if (i, target_column) not in self.obstacles}
            return belief_state.issubset(goal_region) and len(belief_state) > 0
        return False

    def results_and_or(self, state, action):
        if action != 'suck':
            return [self.result(state, action)]
        pos, dirts = state
        res1 = (pos, frozenset(dirts - {pos}))
        x, y = pos
        adjacent_cells = []
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size and (nx, ny) not in self.obstacles:
                adjacent_cells.append((nx, ny))
        if adjacent_cells:
            spilled_cell = random.choice(adjacent_cells)
            new_dirts = frozenset((dirts - {pos}) | {spilled_cell})
            res2 = (pos, new_dirts)
            return [res1, res2] if res1 != res2 else [res1]
        return [res1]

# --- HỆ THỐNG GIẢI THUẬT TOÁN ĐẦY ĐỦ ---
def solve_bfs_1(env):
    start_state = env.get_initial_state()
    start_node = Node(start_state, algo_type='bfs')
    frontier = deque([start_node])
    reached = {start_state}
    steps = 0
    while frontier:
        steps += 1
        node = frontier.popleft()
        if env.is_goal(node.state): return node, steps, len(frontier), len(reached)
        for action in env.get_actions(node.state):
            child_state = env.result(node.state, action)
            if child_state not in reached:
                reached.add(child_state)
                frontier.append(Node(child_state, node, action, node.path_cost + 1, node.depth + 1, algo_type='bfs'))
    return None, steps, len(frontier), len(reached)

def solve_bfs_2(env):
    start_state = env.get_initial_state()
    start_node = Node(start_state, algo_type='bfs')
    if env.is_goal(start_state): return start_node, 1, 0, 1
    frontier = deque([start_node])
    reached = {start_state}
    steps = 0
    while frontier:
        steps += 1
        node = frontier.popleft()
        for action in env.get_actions(node.state):
            child_state = env.result(node.state, action)
            if child_state not in reached:
                child_node = Node(child_state, node, action, node.path_cost + 1, node.depth + 1, algo_type='bfs')
                if env.is_goal(child_state): return child_node, steps, len(frontier), len(reached) + 1
                reached.add(child_state)
                frontier.append(child_node)
    return None, steps, len(frontier), len(reached)

def solve_dfs_1(env):
    start_state = env.get_initial_state()
    start_node = Node(start_state, algo_type='dfs')
    frontier = [start_node]
    reached = {start_state}
    steps = 0
    while frontier:
        steps += 1
        node = frontier.pop()
        if env.is_goal(node.state): return node, steps, len(frontier), len(reached)
        for action in env.get_actions(node.state):
            child_state = env.result(node.state, action)
            if child_state not in reached:
                reached.add(child_state)
                frontier.append(Node(child_state, node, action, node.path_cost + 1, node.depth + 1, algo_type='dfs'))
    return None, steps, len(frontier), len(reached)

def solve_dfs_2(env):
    start_state = env.get_initial_state()
    start_node = Node(start_state, algo_type='dfs')
    if env.is_goal(start_state): return start_node, 1, 0, 1
    frontier = [start_node]
    reached = {start_state}
    steps = 0
    while frontier:
        steps += 1
        node = frontier.pop()
        for action in env.get_actions(node.state):
            child_state = env.result(node.state, action)
            if child_state not in reached:
                child_node = Node(child_state, node, action, node.path_cost + 1, node.depth + 1, algo_type='dfs')
                if env.is_goal(child_state): return child_node, steps, len(frontier), len(reached) + 1
                reached.add(child_state)
                frontier.append(child_node)
    return None, steps, len(frontier), len(reached)

def solve_ids(env):
    start_state = env.get_initial_state()
    total_steps, total_reached = 0, 0
    for depth_limit in range(100):
        start_node = Node(start_state, algo_type='ids')
        frontier = [start_node]
        while frontier:
            total_steps += 1
            node = frontier.pop()
            total_reached += 1
            if env.is_goal(node.state): return node, total_steps, len(frontier), total_reached
            if node.depth < depth_limit:
                for action in env.get_actions(node.state):
                    child_state = env.result(node.state, action)
                    frontier.append(Node(child_state, node, action, node.path_cost + 1, node.depth + 1, algo_type='ids'))
    return None, total_steps, 0, total_reached

def solve_ucs(env):
    start_state = env.get_initial_state()
    start_node = Node(start_state, path_cost=0, algo_type='ucs')
    frontier = []
    heapq.heappush(frontier, (0, start_node))
    reached = {start_state: 0}
    steps = 0
    while frontier:
        steps += 1
        cost, node = heapq.heappop(frontier)
        if env.is_goal(node.state): return node, steps, len(frontier), len(reached)
        for action in env.get_actions(node.state):
            child_state = env.result(node.state, action)
            new_cost = node.path_cost + 1
            if child_state not in reached or new_cost < reached[child_state]:
                reached[child_state] = new_cost
                child_node = Node(child_state, node, action, new_cost, node.depth + 1, algo_type='ucs')
                heapq.heappush(frontier, (new_cost, child_node))
    return None, steps, len(frontier), len(reached)

def solve_greedy(env):
    start_state = env.get_initial_state()
    start_node = Node(start_state, path_cost=0, algo_type='greedy') 
    frontier = []
    h_start = calc_heuristic(start_state)
    heapq.heappush(frontier, (h_start, start_node))
    reached = {start_state: h_start}
    steps = 0
    while frontier:
        steps += 1
        h_val, node = heapq.heappop(frontier)
        if env.is_goal(node.state): return node, steps, len(frontier), len(reached)
        for action in env.get_actions(node.state):
            child_state = env.result(node.state, action)
            h_child = calc_heuristic(child_state)
            if child_state not in reached or h_child < reached[child_state]:
                reached[child_state] = h_child
                child_node = Node(child_state, node, action, path_cost=node.path_cost + 1, depth=node.depth + 1, algo_type='greedy')
                heapq.heappush(frontier, (h_child, child_node))
    return None, steps, len(frontier), len(reached)

def solve_astar(env):
    start_state = env.get_initial_state()
    start_node = Node(start_state, path_cost=0, algo_type='astar')
    frontier = []
    heapq.heappush(frontier, (calc_heuristic(start_state), start_node))
    reached = {start_state: 0}
    steps = 0
    while frontier:
        steps += 1
        f_val, node = heapq.heappop(frontier)
        if env.is_goal(node.state): return node, steps, len(frontier), len(reached)
        for action in env.get_actions(node.state):
            child_state = env.result(node.state, action)
            new_g = node.path_cost + 1
            if child_state not in reached or new_g < reached[child_state]:
                reached[child_state] = new_g
                child_node = Node(child_state, node, action, path_cost=new_g, depth=node.depth + 1, algo_type='astar')
                heapq.heappush(frontier, (new_g + calc_heuristic(child_state), child_node))
    return None, steps, len(frontier), len(reached)

def solve_idastar(env):
    start_state = env.get_initial_state()
    start_node = Node(start_state, path_cost=0, algo_type='idastar')
    threshold = calc_heuristic(start_state)
    total_loops = 0
    total_reached = set()

    def dfs_contour(node, g, f_limit, path_set):
        # FIX: Dung set O(1) thay vi duyet chain parent O(depth)
        nonlocal total_loops
        total_loops += 1
        total_reached.add(node.state)
        if node.f_eval > f_limit: return node.f_eval, None
        if env.is_goal(node.state): return -1, node
        min_cutoff = float('inf')
        for action in env.get_actions(node.state):
            child_state = env.result(node.state, action)
            if child_state in path_set:
                continue
            child_node = Node(child_state, node, action, g + 1, node.depth + 1, algo_type='idastar')
            path_set.add(child_state)
            t, b_node = dfs_contour(child_node, g + 1, f_limit, path_set)
            path_set.discard(child_state)
            if t == -1: return -1, b_node
            if t < min_cutoff: min_cutoff = t
        return min_cutoff, None

    while threshold != float('inf'):
        path_set = {start_state}
        res_t, solved_node = dfs_contour(start_node, 0, threshold, path_set)
        if res_t == -1: return solved_node, total_loops, 0, len(total_reached)
        if res_t == float('inf'): break
        threshold = res_t
        if total_loops > IDA_STAR_MAX_LOOPS: break
    return None, total_loops, 0, len(total_reached)

def solve_simple_hill_climbing(env):
    start_state = env.get_initial_state()
    current_node = Node(start_state, path_cost=0, algo_type='shill')
    steps, reached_count = 0, 1
    while True:
        steps += 1
        if env.is_goal(current_node.state): return current_node, steps, 0, reached_count
        current_h = calc_heuristic(current_node.state)
        improved = False
        for action in env.get_actions(current_node.state):
            next_state = env.result(current_node.state, action)
            reached_count += 1
            if calc_heuristic(next_state) < current_h:
                current_node = Node(next_state, current_node, action, current_node.path_cost + 1, algo_type='shill')
                improved = True
                break
        if not improved: return current_node, steps, 0, reached_count

def solve_steepest_hill_climbing(env):
    start_state = env.get_initial_state()
    current_node = Node(start_state, path_cost=0, algo_type='sthill')
    steps, reached_count = 0, 1
    while True:
        steps += 1
        if env.is_goal(current_node.state): return current_node, steps, 0, reached_count
        current_h = calc_heuristic(current_node.state)
        best_h = current_h
        best_successor = None
        for action in env.get_actions(current_node.state):
            next_state = env.result(current_node.state, action)
            next_h = calc_heuristic(next_state)
            reached_count += 1
            if next_h < best_h:
                best_h = next_h
                best_successor = (next_state, action)
        if best_successor:
            next_state, action = best_successor
            current_node = Node(next_state, current_node, action, current_node.path_cost + 1, algo_type='sthill')
        else: return current_node, steps, 0, reached_count

def solve_stochastic_hill_climbing(env):
    start_state = env.get_initial_state()
    current_node = Node(start_state, path_cost=0, algo_type='stochill')
    steps, reached_count = 0, 1
    while True:
        steps += 1
        if env.is_goal(current_node.state): return current_node, steps, 0, reached_count
        current_h = calc_heuristic(current_node.state)
        better_successors = []
        for action in env.get_actions(current_node.state):
            next_state = env.result(current_node.state, action)
            reached_count += 1
            if calc_heuristic(next_state) < current_h: better_successors.append((next_state, action))
        if better_successors:
            next_state, action = random.choice(better_successors)
            current_node = Node(next_state, current_node, action, current_node.path_cost + 1, algo_type='stochill')
        else: return current_node, steps, 0, reached_count

def solve_random_restart_hill_climbing(env, max_restarts=12):
    total_steps, total_reached = 0, 0
    res_node, steps, _, reached = solve_steepest_hill_climbing(env)
    total_steps += steps
    total_reached += reached
    if env.is_goal(res_node.state):
        res_node.algo_type = 'rrhill'
        return res_node, total_steps, 0, total_reached
    all_cells = [(i, j) for i in range(env.size) for j in range(env.size) if (i, j) not in env.obstacles]
    for r_idx in range(max_restarts):
        if not all_cells: break
        random_pos = random.choice(all_cells)
        restart_state = (random_pos, res_node.state[1])
        restart_node = Node(restart_state, parent=res_node, action=f"restart_to_{random_pos}", path_cost=res_node.path_cost + 1, algo_type='rrhill')
        curr_node = restart_node
        while True:
            total_steps += 1
            if env.is_goal(curr_node.state): return curr_node, total_steps, 0, total_reached
            current_h = calc_heuristic(curr_node.state)
            best_h = current_h
            best_successor = None
            for action in env.get_actions(curr_node.state):
                next_state = env.result(curr_node.state, action)
                next_h = calc_heuristic(next_state)
                total_reached += 1
                if next_h < best_h:
                    best_h = next_h
                    best_successor = (next_state, action)
            if best_successor:
                next_state, action = best_successor
                curr_node = Node(next_state, curr_node, action, curr_node.path_cost + 1, algo_type='rrhill')
            else:
                res_node = curr_node
                break
    return res_node, total_steps, 0, total_reached

def solve_local_beam_search(env, k=4):
    start_state = env.get_initial_state()
    start_node = Node(start_state, algo_type='beams')
    current_beam = [start_node]
    steps, total_reached = 0, 1
    reached_states = {start_state}
    max_iterations = BEAM_SEARCH_MAX_ITER
    while steps < max_iterations:
        steps += 1
        for node in current_beam:
            if env.is_goal(node.state): return node, steps, len(current_beam), total_reached
        successors = []
        for node in current_beam:
            for action in env.get_actions(node.state):
                next_state = env.result(node.state, action)
                if next_state not in reached_states:
                    reached_states.add(next_state)
                    total_reached += 1
                    child_node = Node(next_state, node, action, node.path_cost + 1, algo_type='beams')
                    successors.append(child_node)
        if not successors: break
        successors.sort(key=lambda n: calc_heuristic(n.state))
        current_beam = successors[:k]
    current_beam.sort(key=lambda n: calc_heuristic(n.state))
    return current_beam[0], steps, len(current_beam), total_reached

def solve_simulated_annealing(env):
    start_state = env.get_initial_state()
    current_node = Node(start_state, algo_type='anneal')
    T, T_min, alpha = 10.0, 0.001, 0.995
    steps, total_reached = 0, 1
    while T > T_min:
        steps += 1
        if env.is_goal(current_node.state): return current_node, steps, 0, total_reached
        actions = env.get_actions(current_node.state)
        if not actions: break
        action = random.choice(actions)
        next_state = env.result(current_node.state, action)
        total_reached += 1
        delta = calc_heuristic(next_state) - calc_heuristic(current_node.state)
        next_node = Node(next_state, current_node, action, current_node.path_cost + 1, algo_type='anneal')
        if delta < 0: current_node = next_node
        else:
            try: p = math.exp(-delta / T)
            except OverflowError: p = 0.0
            if random.random() < p: current_node = next_node
        T = alpha * T
    return current_node, steps, 0, total_reached

def solve_belief_state_bfs2(env, case_type):
    if case_type == 'blind1':
        start_belief = frozenset((i, j) for i in range(env.size) for j in range(env.size) if (i, j) not in env.obstacles)
    elif case_type == 'blind2':
        start_belief = frozenset([(0, 0)])
    elif case_type == 'blind3':
        start_belief = frozenset((i, j) for i in range(env.size) for j in range(env.size // 2 + 1) if (i, j) not in env.obstacles)
        
    start_node = Node(start_belief, algo_type=case_type)
    if env.is_goal_belief(start_belief, case_type): return start_node, 1, 0, 1
    frontier = deque([start_node])
    reached = {start_belief}
    steps = 0
    while frontier:
        steps += 1
        node = frontier.popleft()
        for action in env.get_actions():
            child_belief = env.transition_belief(node.state, action)
            if child_belief not in reached:
                child_node = Node(child_belief, node, action, node.path_cost + 1, node.depth + 1, algo_type=case_type)
                if env.is_goal_belief(child_belief, case_type):
                    return child_node, steps, len(frontier), len(reached) + 1
                reached.add(child_belief)
                frontier.append(child_node)
    return None, steps, len(frontier), len(reached)

# ==============================================================================
# THUẬT TOÁN AND-OR GRAPH SEARCH
# ==============================================================================
def solve_and_or_graph_search(env):
    start_state = env.get_initial_state()
    total_loops, total_states_explored = 0, set()

    def or_search(state, path):
        nonlocal total_loops
        total_loops += 1
        total_states_explored.add(state)
        if env.is_goal(state): return []
        if state in path: return "failure"
        for action in env.get_actions(state):
            plan = and_search(env.results_and_or(state, action), path + [state])
            if plan != "failure": return [action, plan]
        return "failure"

    def and_search(states, path):
        plan = {}
        for state in states:
            subplan = or_search(state, path)
            if subplan == "failure": return "failure"
            plan[state] = subplan
        return plan

    result_plan = or_search(start_state, [])
    if result_plan != "failure":
        dummy_node = Node(start_state, algo_type='and_or')
        dummy_node.conditional_plan = result_plan
        return dummy_node, total_loops, 0, len(total_states_explored)
    return None, total_loops, 0, len(total_states_explored)

def get_solution_nodes(node):
    nodes = []
    curr = node
    while curr:
        nodes.append(curr)
        curr = curr.parent
    return nodes[::-1]

def draw_multiline_text(screen, text, x, y, max_width, font_obj, color_obj):
    words = text.split(' ')
    lines, current_line = [], ""
    for word in words:
        test_line = current_line + word + " "
        if font_obj.size(test_line)[0] < max_width: current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    curr_y = y
    for line in lines:
        txt_surf = font_obj.render(line.strip(), True, color_obj)
        screen.blit(txt_surf, (x, curr_y))
        curr_y += font_obj.get_linesize() + 2
    return curr_y

class Button:
    def __init__(self, x, y, w, h, text, color, action_type):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.action_type = action_type

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
        txt = font_small.render(self.text, True, BLACK if self.color != DARK_GRAY else WHITE)
        screen.blit(txt, (self.rect.x + (self.rect.w - txt.get_width())//2, self.rect.y + (self.rect.h - txt.get_height())//2))

def main():
    env_size, num_dirt = 4, 3
    env = Environment(env_size, num_dirt)
    csp_sim = None
    queens_sim = None   # NEW: 8-Queens simulator
    ttt_sim = None       # NEW: Tic-Tac-Toe simulator
    
    buttons = [
        Button(690, 15, 65, 23, "BFS 1", GREEN, "bfs1"),
        Button(760, 15, 65, 23, "BFS 2", GREEN, "bfs2"),
        Button(830, 15, 65, 23, "DFS 1", ORANGE, "dfs1"),
        Button(900, 15, 65, 23, "DFS 2", ORANGE, "dfs2"),
        Button(970, 15, 65, 23, "IDS", YELLOW, "ids"),
        Button(1040, 15, 65, 23, "UCS", BLUE, "ucs"),
        
        Button(690, 44, 60, 23, "Greedy", PURPLE, "greedy"),
        Button(755, 44, 45, 23, "A*", RED, "astar"),
        Button(805, 44, 50, 23, "IDA*", PINK, "idastar"),
        Button(860, 44, 60, 23, "S-HillC", GRAY, "shill"),
        Button(925, 44, 60, 23, "St-HillC", GRAY, "sthill"),
        Button(990, 44, 65, 23, "Stoch-HillC", GRAY, "stochill"),
        Button(1060, 44, 65, 23, "RR-HillC", CYAN, "rrhill"),
        Button(1130, 44, 60, 23, "BeamSearch", PURPLE, "beams"),
        Button(1195, 44, 75, 23, "SimAnneal", PINK, "anneal"),
        
        Button(690, 73, 110, 23, "BLIND-1 (Goal)", CYAN, "blind1"),
        Button(805, 73, 110, 23, "BLIND-2 (Start)", CYAN, "blind2"),
        Button(920, 73, 115, 23, "BLIND-3 (Partial)", CYAN, "blind3"),
        Button(1040, 73, 135, 23, "AND-OR Graph Search", ORANGE, "and_or"),
        
        Button(1180, 73, 135, 23, "HCMC MAP CSP", PURPLE, "hcmc_csp"),

        # NEW: 8-Queens CSP buttons (hàng mới dưới hàng cũ)
        Button(690, 197, 130, 23, "8Q-Simple BT", (180, 100, 220), "q8_simple"),
        Button(825, 197, 130, 23, "8Q-MRV", (220, 140, 60), "q8_mrv"),
        Button(960, 197, 155, 23, "8Q-Forward Check", (60, 180, 160), "q8_fc"),

        # NEW: Tic-Tac-Toe Game-tree buttons
        Button(690, 226, 130, 23, "TTT-Minimax", (60, 130, 200), "ttt_minimax"),
        Button(825, 226, 130, 23, "TTT-AlphaBeta", (200, 90, 60), "ttt_alphabeta"),
        Button(960, 226, 155, 23, "TTT-Expectimax", (120, 180, 60), "ttt_expectimax"),
        
        Button(690, 255, 170, 28, "START SIMULATION", GREEN, "start"),
        Button(875, 255, 170, 28, "RESET MAP", RED, "reset"),
        
        Button(820, 288, 30, 20, "+", GRAY, "inc_size"),
        Button(860, 288, 30, 20, "-", GRAY, "dec_size"),
        Button(1020, 288, 30, 20, "+", GRAY, "inc_dirt"),
        Button(1060, 288, 30, 20, "-", GRAY, "dec_dirt"),
        
        Button(690, 318, 170, 25, "< PREV STEP", BLUE, "prev_step"),
        Button(875, 318, 170, 25, "NEXT STEP >", BLUE, "next_step")
    ]

    selected_algo = "bfs1"
    solution_nodes, animation_index = [], -1
    is_playing = False
    last_update_time = pygame.time.get_ticks()
    algo_stats = {"steps": 0, "frontier": 0, "reached": 0, "status": "Ready", "path_len": 0}
    clock = pygame.time.Clock()

    and_or_execution_path, and_or_current_plan = [], None

    while True:
        try:
            screen.fill(DARK_GRAY)
        
            if selected_algo in ("q8_simple", "q8_mrv", "q8_fc", "ttt_minimax", "ttt_alphabeta", "ttt_expectimax"):
                pass  # 8-Queens / Tic-Tac-Toe: không vẽ grid vacuum hay HCMC map ở đây
            elif selected_algo == "hcmc_csp":
                pygame.draw.rect(screen, LIGHT_BLACK, (30, 60, 620, 680), border_radius=8)
                pygame.draw.rect(screen, GRAY, (30, 60, 620, 680), 2, border_radius=8)
                screen.blit(font_bold.render("SƠ ĐỒ RÀNG BUỘC KỀ NHAU - CÁC QUẬN TP.HCM (CSP)", True, WHITE), (50, 80))
            
                for q_name, info in QUAN_DATA.items():
                    x1, y1 = info["pos"][0] + info["w"]//2, info["pos"][1] + info["h"]//2
                    for adj_q in info["adj"]:
                        if adj_q in QUAN_DATA:
                            x2, y2 = QUAN_DATA[adj_q]["pos"][0] + QUAN_DATA[adj_q]["w"]//2, QUAN_DATA[adj_q]["pos"][1] + QUAN_DATA[adj_q]["h"]//2
                            pygame.draw.line(screen, GRAY, (x1, y1), (x2, y2), 1)
            
                for q_name, info in QUAN_DATA.items():
                    px, py = info["pos"]
                    pw, ph = info["w"], info["h"]
                    block_color = WHITE
                    if csp_sim:
                        if q_name in csp_sim.assignment: 
                            block_color = MAP_COLORS[csp_sim.assignment[q_name]]
                        elif q_name == csp_sim.current_variable: 
                            block_color = YELLOW
                
                    pygame.draw.rect(screen, block_color, (px, py, pw, ph), border_radius=6)
                    b_w = 3 if csp_sim and q_name == csp_sim.current_variable else 1
                    pygame.draw.rect(screen, BLACK, (px, py, pw, ph), b_w, border_radius=6)
                
                    screen.blit(font_small.render(q_name, True, BLACK), (px + (pw - font_small.size(q_name)[0])//2, py + ph//5))
                    d_len = len(csp_sim.domains[q_name]) if csp_sim else 4
                    d_str = f"D: {d_len} màu"
                    screen.blit(font_small.render(d_str, True, DARK_GRAY), (px + (pw - font_small.size(d_str)[0])//2, py + 3*ph//5))
            else:
                grid_area_size = 620
                cell_size = grid_area_size // env.size
                offset_x, offset_y = 30, 60
            
                for i in range(env.size):
                    for j in range(env.size):
                        rect = pygame.Rect(offset_x + j * cell_size, offset_y + i * cell_size, cell_size, cell_size)
                        pygame.draw.rect(screen, WHITE, rect)
                        pygame.draw.rect(screen, BLACK, rect, 1)
                        if (i, j) in env.obstacles: pygame.draw.rect(screen, BLACK, rect)
            
                is_blind_mode = selected_algo in ['blind1', 'blind2', 'blind3']
                current_beliefs = None
            
                if selected_algo == 'and_or' and animation_index != -1:
                    curr_agent_pos, curr_dirts = and_or_execution_path[animation_index] if animation_index < len(and_or_execution_path) else and_or_execution_path[-1]
                elif animation_index == -1:
                    if is_blind_mode:
                        if selected_algo == 'blind1': current_beliefs = set((i, j) for i in range(env.size) for j in range(env.size) if (i, j) not in env.obstacles)
                        elif selected_algo == 'blind2': current_beliefs = {(0,0)}
                        elif selected_algo == 'blind3': current_beliefs = set((i, j) for i in range(env.size) for j in range(env.size // 2 + 1) if (i, j) not in env.obstacles)
                        curr_agent_pos, curr_dirts = None, env.dirt_positions
                    else:
                        curr_agent_pos, curr_dirts = env.agent_pos, env.dirt_positions
                else:
                    curr_node = solution_nodes[animation_index]
                    if is_blind_mode:
                        current_beliefs = curr_node.state
                        curr_agent_pos, curr_dirts = None, env.dirt_positions
                    else:
                        curr_agent_pos, curr_dirts = curr_node.state
                
                for (dx, dy) in curr_dirts:
                    bx, by = offset_x + dy * cell_size + cell_size // 4, offset_y + dx * cell_size + cell_size // 4
                    pygame.draw.ellipse(screen, GRAY, (bx, by, cell_size // 2, cell_size // 2))
                    pygame.draw.circle(screen, BLACK, (bx + cell_size//4, by + cell_size//4), 3)

                if not is_blind_mode and curr_agent_pos:
                    rx, ry = offset_x + curr_agent_pos[1] * cell_size + cell_size // 6, offset_y + curr_agent_pos[0] * cell_size + cell_size // 6
                    pygame.draw.rect(screen, BLUE, (rx, ry, 2 * cell_size // 3, 2 * cell_size // 3), border_radius=10)
                    pygame.draw.circle(screen, YELLOW, (rx + cell_size // 3, ry + cell_size // 3), cell_size // 8)
                elif is_blind_mode and current_beliefs:
                    for (bx, by) in current_beliefs:
                        rx, ry = offset_x + by * cell_size + cell_size // 6, offset_y + bx * cell_size + cell_size // 6
                        pygame.draw.rect(screen, CYAN, (rx, ry, 2 * cell_size // 3, 2 * cell_size // 3), width=3, border_radius=8)
                        pygame.draw.circle(screen, RED, (rx + cell_size // 3, ry + cell_size // 3), cell_size // 12)

            # NEW: AI tự động đi khi đến lượt AI trong Tic-Tac-Toe
            if selected_algo in ("ttt_minimax", "ttt_alphabeta", "ttt_expectimax") and ttt_sim:
                if ttt_sim.turn == TTT_AI and not ttt_sim.game_over and not ttt_sim.ai_thinking_done:
                    if pygame.time.get_ticks() - last_update_time > 400:
                        ttt_sim.ai_move()
                        algo_stats["steps"] = ttt_sim.nodes_explored
                        algo_stats["reached"] = ttt_sim.pruned_branches if ttt_sim.strategy == "alphabeta" else ttt_sim.nodes_explored
                        if ttt_sim.game_over:
                            algo_stats["status"] = f"Kết quả: {'HÒA' if ttt_sim.winner=='draw' else ttt_sim.winner + ' THẮNG'}"
                        else:
                            algo_stats["status"] = "Lượt bạn (X)"
                        last_update_time = pygame.time.get_ticks()

            if is_playing and pygame.time.get_ticks() - last_update_time > 600:
                if selected_algo == "hcmc_csp":
                    if csp_sim:
                        done_csp = csp_sim.step()
                        if done_csp: is_playing = False
                    last_update_time = pygame.time.get_ticks()
                elif selected_algo in ("q8_simple", "q8_mrv", "q8_fc"):
                    if queens_sim and not queens_sim.done:
                        queens_sim.step()
                        algo_stats["steps"] = queens_sim.nodes_explored
                        algo_stats["reached"] = queens_sim.backtracks
                        if queens_sim.done:
                            is_playing = False
                            algo_stats["status"] = "Tìm được lời giải!" if queens_sim.success else "Không có lời giải!"
                    last_update_time = pygame.time.get_ticks()
                elif selected_algo == 'and_or':
                    if animation_index != -1:
                        current_state = and_or_execution_path[-1]
                        if env.is_goal(current_state):
                            is_playing = False
                            algo_stats["status"] = "Success! Goal Reached."
                        elif and_or_current_plan == "failure" or not and_or_current_plan or not isinstance(and_or_current_plan, list):
                            is_playing = False
                            algo_stats["status"] = "Plan broken!"
                        else:
                            action, subplan = and_or_current_plan[0], and_or_current_plan[1]
                            possible_results = env.results_and_or(current_state, action)
                            next_state = random.choice(possible_results)
                        
                            and_or_execution_path.append(next_state)
                            animation_index += 1
                        
                            if isinstance(subplan, dict) and next_state in subplan:
                                and_or_current_plan = subplan[next_state]
                            else:
                                and_or_current_plan = "failure"
                            
                            last_update_time = pygame.time.get_ticks()
                else:
                    if animation_index < len(solution_nodes) - 1:
                        animation_index += 1
                        last_update_time = pygame.time.get_ticks()
                    else:
                        is_playing = False
                        if is_blind_mode: algo_stats["status"] = "Success! Belief Converged."
                        else: algo_stats["status"] = "Success! Goal Reached." if env.is_goal(solution_nodes[-1].state) else "Stuck in Optimum!"

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for btn in buttons:
                        if btn.rect.collidepoint(mouse_pos):
                            if btn.action_type in ["bfs1", "bfs2", "dfs1", "dfs2", "ids", "ucs", "greedy", "astar", "idastar", "shill", "sthill", "stochill", "rrhill", "beams", "anneal", "blind1", "blind2", "blind3", "and_or", "hcmc_csp", "q8_simple", "q8_mrv", "q8_fc", "ttt_minimax", "ttt_alphabeta", "ttt_expectimax"]:
                                selected_algo = btn.action_type
                                animation_index, solution_nodes = -1, []
                                is_playing = False
                                if selected_algo == "hcmc_csp":
                                    csp_sim = CSPState()
                                elif selected_algo in ("q8_simple", "q8_mrv", "q8_fc"):
                                    strategy_map = {"q8_simple": "simple", "q8_mrv": "mrv", "q8_fc": "fc"}
                                    queens_sim = QueensCSP(strategy=strategy_map[selected_algo])
                                elif selected_algo in ("ttt_minimax", "ttt_alphabeta", "ttt_expectimax"):
                                    ttt_strategy_map = {"ttt_minimax": "minimax", "ttt_alphabeta": "alphabeta", "ttt_expectimax": "expectimax"}
                                    ttt_sim = TicTacToeGame(strategy=ttt_strategy_map[selected_algo])
                                algo_stats["status"] = f"Selected {btn.text}"
                            elif btn.action_type == "inc_size" and env.size < 10:
                                env.size += 1
                                env.generate_map()
                                animation_index, solution_nodes = -1, []
                            elif btn.action_type == "dec_size" and env.size > 3:
                                env.size -= 1
                                env.generate_map()
                                animation_index, solution_nodes = -1, []
                            elif btn.action_type == "inc_dirt" and env.num_dirt < 15:
                                env.num_dirt += 1
                                env.generate_map()
                                animation_index, solution_nodes = -1, []
                            elif btn.action_type == "dec_dirt" and env.num_dirt > 1:
                                env.num_dirt -= 1
                                env.generate_map()
                                animation_index, solution_nodes = -1, []
                            elif btn.action_type == "reset":
                                env.generate_map()
                                if selected_algo == "hcmc_csp":
                                    csp_sim = CSPState()
                                elif selected_algo in ("q8_simple", "q8_mrv", "q8_fc"):
                                    strategy_map = {"q8_simple": "simple", "q8_mrv": "mrv", "q8_fc": "fc"}
                                    queens_sim = QueensCSP(strategy=strategy_map[selected_algo])
                                elif selected_algo in ("ttt_minimax", "ttt_alphabeta", "ttt_expectimax"):
                                    ttt_strategy_map = {"ttt_minimax": "minimax", "ttt_alphabeta": "alphabeta", "ttt_expectimax": "expectimax"}
                                    if ttt_sim: ttt_sim.reset()
                                    else: ttt_sim = TicTacToeGame(strategy=ttt_strategy_map[selected_algo])
                                solution_nodes, and_or_execution_path = [], []
                                animation_index, is_playing = -1, False
                                algo_stats = {"steps": 0, "frontier": 0, "reached": 0, "status": "Map Reset", "path_len": 0}
                            elif btn.action_type == "start":
                                if selected_algo == "hcmc_csp":
                                    csp_sim = CSPState()
                                    is_playing = True
                                    algo_stats["status"] = "CSP Backtracking..."
                                elif selected_algo in ("q8_simple", "q8_mrv", "q8_fc"):
                                    strategy_map = {"q8_simple": "simple", "q8_mrv": "mrv", "q8_fc": "fc"}
                                    queens_sim = QueensCSP(strategy=strategy_map[selected_algo])
                                    is_playing = True
                                    algo_stats["status"] = f"8-Queens [{strategy_map[selected_algo].upper()}] Running..."
                                elif selected_algo in ("ttt_minimax", "ttt_alphabeta", "ttt_expectimax"):
                                    ttt_strategy_map = {"ttt_minimax": "minimax", "ttt_alphabeta": "alphabeta", "ttt_expectimax": "expectimax"}
                                    ttt_sim = TicTacToeGame(strategy=ttt_strategy_map[selected_algo])
                                    algo_stats["status"] = f"Tic-Tac-Toe [{ttt_strategy_map[selected_algo].upper()}] – Lượt bạn (X)"
                                else:
                                    algo_stats["status"] = "Computing..."
                                    if selected_algo == "bfs1": res, s, f, r = solve_bfs_1(env)
                                    elif selected_algo == "bfs2": res, s, f, r = solve_bfs_2(env)
                                    elif selected_algo == "dfs1": res, s, f, r = solve_dfs_1(env)
                                    elif selected_algo == "dfs2": res, s, f, r = solve_dfs_2(env)
                                    elif selected_algo == "ids": res, s, f, r = solve_ids(env)
                                    elif selected_algo == "ucs": res, s, f, r = solve_ucs(env)
                                    elif selected_algo == "greedy": res, s, f, r = solve_greedy(env)
                                    elif selected_algo == "astar": res, s, f, r = solve_astar(env)
                                    elif selected_algo == "idastar": res, s, f, r = solve_idastar(env)
                                    elif selected_algo == "shill": res, s, f, r = solve_simple_hill_climbing(env)
                                    elif selected_algo == "sthill": res, s, f, r = solve_steepest_hill_climbing(env)
                                    elif selected_algo == "stochill": res, s, f, r = solve_stochastic_hill_climbing(env)
                                    elif selected_algo == "rrhill": res, s, f, r = solve_random_restart_hill_climbing(env)
                                    elif selected_algo == "beams": res, s, f, r = solve_local_beam_search(env, k=4)
                                    elif selected_algo == "anneal": res, s, f, r = solve_simulated_annealing(env)
                                    elif selected_algo in ["blind1", "blind2", "blind3"]: res, s, f, r = solve_belief_state_bfs2(env, selected_algo)
                                    elif selected_algo == "and_or": res, s, f, r = solve_and_or_graph_search(env)
                                    
                                    if res:
                                        if selected_algo == 'and_or':
                                            and_or_execution_path = [env.get_initial_state()]
                                            and_or_current_plan = res.conditional_plan
                                            animation_index, is_playing = 0, True
                                            algo_stats = {"steps": s, "frontier": 0, "reached": r, "status": "And-Or Plan Executing...", "path_len": "Tree Branch"}
                                        else:
                                            solution_nodes = get_solution_nodes(res)
                                            for node_item in solution_nodes: node_item.algo_type = selected_algo
                                            animation_index, is_playing = 0, True
                                            algo_stats = {"steps": s, "frontier": f, "reached": r, "status": "Auto-Moving...", "path_len": len(solution_nodes) - 1}
                                        last_update_time = pygame.time.get_ticks()
                                    else:
                                        algo_stats["status"] = "No Solution/Plan Found!"
                            elif btn.action_type == "prev_step":
                                is_playing = False
                                if selected_algo not in ("hcmc_csp", "q8_simple", "q8_mrv", "q8_fc", "ttt_minimax", "ttt_alphabeta", "ttt_expectimax") and len(solution_nodes) > 0 and animation_index > 0:
                                    animation_index -= 1
                            elif btn.action_type == "next_step":
                                is_playing = False
                                if selected_algo == "hcmc_csp" and csp_sim:
                                    csp_sim.step()
                                elif selected_algo in ("q8_simple", "q8_mrv", "q8_fc") and queens_sim:
                                    if not queens_sim.done:
                                        queens_sim.step()
                                elif len(solution_nodes) > 0 and animation_index < len(solution_nodes) - 1:
                                    animation_index += 1

                    # NEW: Xử lý click vào bàn cờ Tic-Tac-Toe (vùng vẽ bên trái, giống 8-Queens)
                    if selected_algo in ("ttt_minimax", "ttt_alphabeta", "ttt_expectimax") and ttt_sim:
                        ttt_bx0, ttt_by0, ttt_cell = 110, 140, 130  # phải khớp với phần render bên dưới
                        if ttt_sim.turn == TTT_HUMAN and not ttt_sim.game_over:
                            mx, my = pygame.mouse.get_pos()
                            if ttt_bx0 <= mx < ttt_bx0 + 3*ttt_cell and ttt_by0 <= my < ttt_by0 + 3*ttt_cell:
                                col = (mx - ttt_bx0) // ttt_cell
                                row = (my - ttt_by0) // ttt_cell
                                ttt_sim.human_move(row * 3 + col)

            for btn in buttons:
                if btn.action_type == selected_algo: pygame.draw.rect(screen, WHITE, btn.rect.inflate(4, 4), 2, border_radius=6)
                btn.draw(screen)

            screen.blit(font.render(f"Matrix Size: {env.size}x{env.size}", True, WHITE), (690, 288))
            screen.blit(font.render(f"Dirt Count: {env.num_dirt}", True, WHITE), (915, 288))

            # PANEL REAL-TIME LOGS THUẬT TOÁN
            panel_x, panel_y, panel_w, panel_h = 680, 354, 640, 401
            pygame.draw.rect(screen, LIGHT_BLACK, (panel_x, panel_y, panel_w, panel_h), border_radius=8)
            pygame.draw.rect(screen, GRAY, (panel_x, panel_y, panel_w, panel_h), 2, border_radius=8)
        
            if selected_algo in ("q8_simple", "q8_mrv", "q8_fc"):
                # ============================================================
                # RENDER 8-QUEENS: Bàn cờ bên trái + Logs bên phải
                # ============================================================
                # -- Vẽ bàn cờ 8×8 (trong khu vực lưới bên trái) --
                board_size = 520
                cell = board_size // N_QUEENS
                bx0, by0 = 50, 80

                strat_names = {"q8_simple": "Simple Backtracking", "q8_mrv": "Backtracking + MRV", "q8_fc": "Backtracking + Forward Checking"}
                screen.blit(font_bold.render(f"8-QUEENS CSP  –  {strat_names[selected_algo]}", True, WHITE), (bx0, by0 - 25))

                for row in range(N_QUEENS):
                    for col in range(N_QUEENS):
                        color = (240, 217, 181) if (row + col) % 2 == 0 else (181, 136, 99)
                        pygame.draw.rect(screen, color, (bx0 + col*cell, by0 + row*cell, cell, cell))

                # Tô màu miền còn hợp lệ (màu nhạt)
                if queens_sim:
                    for col in range(N_QUEENS):
                        if col not in queens_sim.assignment:
                            for row in queens_sim.domains[col]:
                                if queens_sim._is_consistent(col, row):
                                    s_surf = pygame.Surface((cell, cell), pygame.SRCALPHA)
                                    s_surf.fill((100, 200, 100, 60))
                                    screen.blit(s_surf, (bx0 + col*cell, by0 + row*cell))

                # Vẽ quân hậu đã đặt
                if queens_sim:
                    for col, row in queens_sim.assignment.items():
                        cx = bx0 + col*cell + cell//2
                        cy = by0 + row*cell + cell//2
                        pygame.draw.circle(screen, (220, 50, 50), (cx, cy), cell//2 - 4)
                        pygame.draw.circle(screen, WHITE, (cx, cy), cell//2 - 8)
                        screen.blit(font_bold.render("Q", True, (220, 50, 50)), (cx - 8, cy - 9))

                # Vẽ đường kẻ ô
                for i in range(N_QUEENS + 1):
                    pygame.draw.line(screen, BLACK, (bx0, by0 + i*cell), (bx0 + board_size, by0 + i*cell), 1)
                    pygame.draw.line(screen, BLACK, (bx0 + i*cell, by0), (bx0 + i*cell, by0 + board_size), 1)

                # Nhãn cột/hàng
                for i in range(N_QUEENS):
                    screen.blit(font_small.render(str(i), True, CYAN), (bx0 + i*cell + cell//2 - 4, by0 - 16))
                    screen.blit(font_small.render(str(i), True, CYAN), (bx0 - 16, by0 + i*cell + cell//2 - 8))

                # -- Panel log bên phải --
                screen.blit(font_bold.render("LOGS TỪNG BƯỚC:", True, YELLOW), (panel_x + 10, panel_y + 10))
                y_log = panel_y + 35
                if queens_sim:
                    for log in queens_sim.logs[-15:]:
                        clr = GREEN if "Thành công" in log or "✔" in log else (RED if "Backtrack" in log or "✘" in log else WHITE)
                        screen.blit(font_small.render(log[:78], True, clr), (panel_x + 10, y_log))
                        y_log += 18
                    pygame.draw.line(screen, GRAY, (panel_x+10, y_log+4), (panel_x+panel_w-10, y_log+4), 1)
                    y_log += 14
                    screen.blit(font_bold.render("THỐNG KÊ:", True, ORANGE), (panel_x + 10, y_log)); y_log += 22
                    screen.blit(font.render(f"Nodes explored : {queens_sim.nodes_explored}", True, WHITE), (panel_x+10, y_log)); y_log += 20
                    screen.blit(font.render(f"Backtracks     : {queens_sim.backtracks}", True, WHITE), (panel_x+10, y_log)); y_log += 20
                    screen.blit(font.render(f"Queens placed  : {len(queens_sim.assignment)} / 8", True, WHITE), (panel_x+10, y_log)); y_log += 20
                    status_clr = GREEN if queens_sim.success else (RED if queens_sim.done else YELLOW)
                    status_txt = "✔ SOLVED!" if queens_sim.success else ("✘ NO SOLUTION" if queens_sim.done else "Đang giải...")
                    screen.blit(font_bold.render(f"Trạng thái: {status_txt}", True, status_clr), (panel_x+10, y_log))

            elif selected_algo in ("ttt_minimax", "ttt_alphabeta", "ttt_expectimax"):
                # ============================================================
                # RENDER TIC-TAC-TOE: Bàn cờ 3x3 bên trái + Logs game-tree bên phải
                # ============================================================
                ttt_bx0, ttt_by0, ttt_cell = 110, 140, 130   # PHẢI khớp với phần xử lý click ở event handler

                strat_names = {"ttt_minimax": "Minimax", "ttt_alphabeta": "Alpha-Beta Pruning", "ttt_expectimax": "Expectimax (đối thủ ngẫu nhiên)"}
                screen.blit(font_bold.render(f"TIC-TAC-TOE  –  {strat_names[selected_algo]}", True, WHITE), (ttt_bx0 - 30, ttt_by0 - 60))
                screen.blit(font.render("Bạn = X (click vào ô)   |   AI = O", True, GRAY), (ttt_bx0 - 30, ttt_by0 - 35))

                board_px = ttt_cell * 3
                pygame.draw.rect(screen, (245, 245, 235), (ttt_bx0, ttt_by0, board_px, board_px))
                for i in range(1, 3):
                    pygame.draw.line(screen, BLACK, (ttt_bx0 + i*ttt_cell, ttt_by0), (ttt_bx0 + i*ttt_cell, ttt_by0 + board_px), 4)
                    pygame.draw.line(screen, BLACK, (ttt_bx0, ttt_by0 + i*ttt_cell), (ttt_bx0 + board_px, ttt_by0 + i*ttt_cell), 4)
                pygame.draw.rect(screen, BLACK, (ttt_bx0, ttt_by0, board_px, board_px), 3)

                if ttt_sim:
                    for idx, mark in enumerate(ttt_sim.board):
                        row, col = idx // 3, idx % 3
                        cx = ttt_bx0 + col*ttt_cell + ttt_cell//2
                        cy = ttt_by0 + row*ttt_cell + ttt_cell//2
                        if mark == 'X':
                            off = ttt_cell//3
                            pygame.draw.line(screen, (50, 90, 200), (cx-off, cy-off), (cx+off, cy+off), 8)
                            pygame.draw.line(screen, (50, 90, 200), (cx+off, cy-off), (cx-off, cy+off), 8)
                        elif mark == 'O':
                            pygame.draw.circle(screen, (210, 60, 60), (cx, cy), ttt_cell//3, 8)

                    if ttt_sim.game_over:
                        msg = "HÒA!" if ttt_sim.winner == 'draw' else f"{ttt_sim.winner} THẮNG!"
                        clr = YELLOW if ttt_sim.winner == 'draw' else (BLUE if ttt_sim.winner=='X' else RED)
                        screen.blit(font_bold.render(msg, True, clr), (ttt_bx0, ttt_by0 + board_px + 20))
                    else:
                        turn_msg = "Lượt của bạn (X) – Click vào ô trống" if ttt_sim.turn == TTT_HUMAN else "AI (O) đang suy nghĩ..."
                        screen.blit(font.render(turn_msg, True, WHITE), (ttt_bx0, ttt_by0 + board_px + 20))

                screen.blit(font_bold.render("GAME-TREE SEARCH LOGS:", True, YELLOW), (panel_x + 10, panel_y + 10))
                y_log = panel_y + 35
                if ttt_sim:
                    for log in ttt_sim.logs[-15:]:
                        clr = GREEN if "THẮNG" in log or "=>" in log else (ORANGE if "HÒA" in log else WHITE)
                        screen.blit(font_small.render(log[:78], True, clr), (panel_x + 10, y_log))
                        y_log += 18
                    pygame.draw.line(screen, GRAY, (panel_x+10, y_log+4), (panel_x+panel_w-10, y_log+4), 1)
                    y_log += 14
                    screen.blit(font_bold.render("THỐNG KÊ NƯỚC ĐI CUỐI CỦA AI:", True, ORANGE), (panel_x + 10, y_log)); y_log += 22
                    screen.blit(font.render(f"Nodes explored : {ttt_sim.nodes_explored}", True, WHITE), (panel_x+10, y_log)); y_log += 20
                    if ttt_sim.strategy == "alphabeta":
                        screen.blit(font.render(f"Nhánh bị cắt   : {ttt_sim.pruned_branches}", True, WHITE), (panel_x+10, y_log)); y_log += 20
                    eval_str = f"{ttt_sim.last_eval:.2f}" if ttt_sim.last_eval is not None else "N/A"
                    screen.blit(font.render(f"Giá trị nước đi: {eval_str}", True, WHITE), (panel_x+10, y_log)); y_log += 20
                    algo_explain = {
                        "ttt_minimax": "MAX (AI) chọn nước tốt nhất, giả định MIN (bạn) chơi tối ưu chống lại.",
                        "ttt_alphabeta": "Giống Minimax nhưng cắt nhánh không ảnh hưởng kết quả → nhanh hơn.",
                        "ttt_expectimax": "Nút đối thủ là CHANCE (ngẫu nhiên đều), không phải MIN tối ưu."
                    }
                    y_log += 6
                    draw_multiline_text(screen, algo_explain[selected_algo], panel_x+10, y_log, panel_w - 30, font_small, CYAN)

            elif selected_algo == "hcmc_csp":
                screen.blit(font_bold.render("MÔ PHỎNG TỪNG BƯỚC TÌM LỜI GIẢI - CSP", True, YELLOW), (700, panel_y + 10))
                y_pos = panel_y + 35
                if csp_sim:
                    for log in csp_sim.logs[-11:]:
                        screen.blit(font.render(log, True, WHITE), (700, y_pos))
                        y_pos += 22
                    pygame.draw.line(screen, DARK_GRAY, (panel_x + 10, y_pos), (panel_x + panel_w - 10, y_pos), 2)
                    y_pos += 15
                    screen.blit(font_bold.render("BẢNG ĐỐI CHIẾU PHÂN HOẠCH (HIỆN TẠI):", True, GREEN), (700, y_pos))
                    y_pos += 25
                    draw_multiline_text(screen, str(csp_sim.assignment), 700, y_pos, panel_w - 40, font_small, YELLOW)
            else:
                screen.blit(font_bold.render("ALGORITHM REAL-TIME EXECUTION LOGS", True, YELLOW), (700, panel_y + 10))
                curr_step_str = f"{animation_index} / {len(solution_nodes)-1}" if animation_index != -1 and selected_algo != 'and_or' else (f"{animation_index}" if animation_index != -1 else "N/A")
            
                labels = [
                    f"Current Algo Mode: {selected_algo.upper()}",
                    f"Execution Status: {algo_stats['status']}",
                    f"Active Step Position: {curr_step_str}",
                    f"Algorithm Total Loops / Iterations: {algo_stats['steps']}",
                    f"States Processed/Explored Count: {algo_stats['reached']}"
                ]
                y_pos = panel_y + 35
                for label in labels:
                    screen.blit(font.render(label, True, WHITE), (700, y_pos))
                    y_pos += 22

                pygame.draw.line(screen, DARK_GRAY, (panel_x + 10, y_pos), (panel_x + panel_w - 10, y_pos), 2)
                y_pos += 8
            
                screen.blit(font_bold.render("COST PARAMETERS & CONSTRAINTS:", True, ORANGE), (700, y_pos))
                y_pos += 22
                if animation_index != -1:
                    if selected_algo in ['blind1', 'blind2', 'blind3']:
                        c_lbls = [f"Ambiguity Count (Belief Size): {len(solution_nodes[animation_index].state)} states inside", "BFS2 Rule: Checked goal when generating child."]
                    elif selected_algo == 'and_or':
                        c_lbls = ["Model Type: Nondeterministic environment", "Branching structure: Strategy plan (AND-OR Graph)"]
                    else:
                        act_n = solution_nodes[animation_index]
                        c_lbls = [f"g(n) Cost: {act_n.path_cost} | h(n) Heuristic: {calc_heuristic(act_n.state)}"]
                    for cl in c_lbls:
                        screen.blit(font.render(cl, True, WHITE), (700, y_pos)); y_pos += 20
                else:
                    screen.blit(font.render("Run algorithm to visualize cost dynamics.", True, GRAY), (700, y_pos)); y_pos += 20

                y_pos += 5
                pygame.draw.line(screen, DARK_GRAY, (panel_x + 10, y_pos), (panel_x + panel_w - 10, y_pos), 2)
                y_pos += 8
            
                screen.blit(font_bold.render("CURRENT NODE COMPREHENSIVE REPR:", True, GREEN), (700, y_pos))
                y_pos += 22
                if animation_index != -1:
                    repr_str = f"AndOr_State(pos={and_or_execution_path[animation_index][0]}, dirts={list(and_or_execution_path[animation_index][1])})" if selected_algo == 'and_or' else repr(solution_nodes[animation_index])
                    y_pos = draw_multiline_text(screen, repr_str, 700, y_pos, panel_w - 40, font_small, YELLOW)
                else:
                    screen.blit(font.render("No active Node instance available", True, GRAY), (700, y_pos)); y_pos += 22

                y_pos += 5
                pygame.draw.line(screen, DARK_GRAY, (panel_x + 10, y_pos), (panel_x + panel_w - 10, y_pos), 2)
                y_pos += 8
            
                screen.blit(font_bold.render("SOLUTION PATH SEQUENCE (ACTIONS):", True, BLUE), (700, y_pos))
                y_pos += 22
                if selected_algo == 'and_or' and animation_index != -1:
                    draw_multiline_text(screen, f"Strategy sub-tree branch: {str(and_or_current_plan)[:120]}...", 700, y_pos, panel_w - 40, font_small, WHITE)
                elif solution_nodes:
                    acts = [str(n.action) for n in solution_nodes if n.action is not None]
                    draw_multiline_text(screen, " -> ".join(acts) if acts else "No Move Needed (Already Goal)", 700, y_pos, panel_w - 40, font_small, WHITE)
                else:
                    screen.blit(font.render("None (Click START to generate paths)", True, GRAY), (700, y_pos))

        except Exception as e:
            # FIX: Bắt lỗi runtime, hiển thị thay vì crash
            screen.fill(DARK_GRAY)
            msg = font_bold.render('Loi: ' + str(e)[:100], True, RED)
            screen.blit(msg, (20, SCREEN_HEIGHT // 2))
            is_playing = False
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()