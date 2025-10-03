import pygame
import sys
import time

WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // (COLS + 1)

LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)

WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
RED = (220, 0, 0)

def coords_to_cell(row, col):
    letters = "ABCDEFGH"
    numbers = "87654321"
    return f"{letters[col]}{numbers[row]}"

class Piece:
    def __init__(self, row, col, color, king=False):
        self.row = row
        self.col = col
        self.color = color
        self.king = king

    def draw(self, win):
        radius = SQUARE_SIZE // 2 - 10
        x = (self.col+1) * SQUARE_SIZE + SQUARE_SIZE // 2
        y = (self.row+1) * SQUARE_SIZE + SQUARE_SIZE // 2
        pygame.draw.circle(win, self.color, (x, y), radius)
        if self.king:
            pygame.draw.circle(win, RED, (x, y), radius // 2, 2)

    def move(self, row, col):
        self.row = row
        self.col = col
        if self.color == BLACK and row == ROWS - 1:
            self.king = True
        if self.color == WHITE and row == 0:
            self.king = True

class Board:
    def __init__(self):
        self.board = []
        self.create_board()

    def create_board(self):
        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 1:
                    if row < 3:
                        self.board[row][col] = Piece(row, col, BLACK)
                    elif row > 4:
                        self.board[row][col] = Piece(row, col, WHITE)

    def draw(self, win):
        win.fill((200, 170, 120))
        font = pygame.font.SysFont("Arial", 20, bold=True)
        for row in range(ROWS):
            for col in range(COLS):
                rect_x = (col + 1) * SQUARE_SIZE
                rect_y = (row + 1) * SQUARE_SIZE
                color = DARK_SQUARE if (row + col) % 2 == 1 else LIGHT_SQUARE
                pygame.draw.rect(win, color, (rect_x, rect_y, SQUARE_SIZE, SQUARE_SIZE))
        letters = "ABCDEFGH"
        for col in range(COLS):
            label = font.render(letters[col], True, BLACK)
            x = (col + 1) * SQUARE_SIZE + SQUARE_SIZE // 2 - label.get_width() // 2
            win.blit(label, (x, 5))
        numbers = "87654321"
        for row in range(ROWS):
            label = font.render(numbers[row], True, BLACK)
            y = (row + 1) * SQUARE_SIZE + SQUARE_SIZE // 2 - label.get_height() // 2
            win.blit(label, (5, y))
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def move_piece(self, piece, row, col):
        self.board[piece.row][piece.col] = 0
        piece.move(row, col)
        self.board[row][col] = piece

    def remove_piece(self, row, col):
        self.board[row][col] = 0

    def get_piece_moves(self, piece):
        moves = {}
        captures = {}
        if piece.king:
            for dcol, drow in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                r, c = piece.row + drow, piece.col + dcol
                while 0 <= r < ROWS and 0 <= c < COLS:
                    if self.board[r][c] == 0:
                        moves[(r, c)] = None
                    else:
                        if self.board[r][c].color != piece.color:
                            r2, c2 = r + drow, c + dcol
                            while 0 <= r2 < ROWS and 0 <= c2 < COLS and self.board[r2][c2] == 0:
                                captures[(r2, c2)] = (r, c)
                                r2 += drow
                                c2 += dcol
                        break
                    r += drow
                    c += dcol
        else:
            step = -1 if piece.color == WHITE else 1
            directions = [(-1, step), (1, step)]
            for dcol, drow in directions:
                r, c = piece.row + drow, piece.col + dcol
                if 0 <= r < ROWS and 0 <= c < COLS and self.board[r][c] == 0:
                    moves[(r, c)] = None
            for dcol, drow in directions:
                r, c = piece.row + drow, piece.col + dcol
                r2, c2 = piece.row + 2 * drow, piece.col + 2 * dcol
                if (
                    0 <= r2 < ROWS and 0 <= c2 < COLS
                    and self.board[r][c] != 0
                    and self.board[r][c].color != piece.color
                    and self.board[r2][c2] == 0
                ):
                    captures[(r2, c2)] = (r, c)
        return moves, captures

    def get_all_moves(self, color, forced_piece=None):
        normal_moves = {}
        capture_moves = {}

        if forced_piece is not None:
            r, c = forced_piece
            p = self.board[r][c]
            if p != 0 and p.color == color:
                _, captures = self.get_piece_moves(p)
                if captures:
                    capture_moves[p] = captures
            return capture_moves, bool(capture_moves)

        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0 and piece.color == color:
                    moves, captures = self.get_piece_moves(piece)
                    if captures:
                        capture_moves[piece] = captures
                    elif moves:
                        normal_moves[piece] = moves

        return capture_moves if capture_moves else normal_moves, bool(capture_moves)

    def has_pieces_and_moves(self, color):
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0 and piece.color == color:
                    moves, captures = self.get_piece_moves(piece)
                    if moves or captures:
                        return True
        return False

def evaluate(board):
    score = 0
    for row in range(ROWS):
        for col in range(COLS):
            piece = board.board[row][col]
            if piece != 0:
                val = 100
                if piece.king:
                    val += 120
                if piece.color == BLACK:
                    val += piece.row * 10
                else:
                    val += (ROWS - 1 - piece.row) * 10
                if 2 <= row <= 5 and 2 <= col <= 5:
                    val += 5
                if row in [0, ROWS - 1]:
                    val += 15
                neighbors = 0
                for dr in [-1, 1]:
                    for dc in [-1, 1]:
                        r, c = row + dr, col + dc
                        if 0 <= r < ROWS and 0 <= c < COLS:
                            q = board.board[r][c]
                            if q != 0 and q.color == piece.color:
                                neighbors += 1
                if neighbors == 0:
                    val -= 10
                piece_score = val if piece.color == WHITE else -val
                score += piece_score
    return score

def minimax(board, depth, alpha, beta, maximizing, start_time, time_limit=1.0, forced_piece=None):
    if depth == 0 or time.time() - start_time > time_limit:
        return evaluate(board), None

    color = WHITE if maximizing else BLACK
    all_moves, only_captures = board.get_all_moves(color, forced_piece=forced_piece)

    if not all_moves:
        return evaluate(board), None

    best_move = None

    if maximizing:
        max_eval = -1e9
        for piece, moves in all_moves.items():
            for move, captured in moves.items():
                new_board = clone_board(board)

                if captured:
                    new_board.remove_piece(*captured)

                new_piece = Piece(piece.row, piece.col, piece.color, piece.king)
                new_board.move_piece(new_piece, *move)

                _, next_caps = new_board.get_piece_moves(new_piece)
                if captured and next_caps:
                    next_depth = depth
                    next_maximizing = maximizing
                    next_forced = (new_piece.row, new_piece.col)
                else:
                    next_depth = depth - 1
                    next_maximizing = not maximizing
                    next_forced = None

                eval_score, _ = minimax(new_board, next_depth, alpha, beta, next_maximizing,
                                        start_time, time_limit, forced_piece=next_forced)

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = (piece, move, captured)

                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
        return max_eval, best_move
    else:
        min_eval = 1e9
        for piece, moves in all_moves.items():
            for move, captured in moves.items():
                new_board = clone_board(board)

                if captured:
                    new_board.remove_piece(*captured)

                new_piece = Piece(piece.row, piece.col, piece.color, piece.king)
                new_board.move_piece(new_piece, *move)

                _, next_caps = new_board.get_piece_moves(new_piece)
                if captured and next_caps:
                    next_depth = depth
                    next_maximizing = maximizing
                    next_forced = (new_piece.row, new_piece.col)
                else:
                    next_depth = depth - 1
                    next_maximizing = not maximizing
                    next_forced = None

                eval_score, _ = minimax(new_board, next_depth, alpha, beta, next_maximizing,
                                        start_time, time_limit, forced_piece=next_forced)

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = (piece, move, captured)

                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
        return min_eval, best_move

def clone_board(board):
    new_b = Board()
    new_b.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    for r in range(ROWS):
        for c in range(COLS):
            p = board.board[r][c]
            if p != 0:
                new_b.board[r][c] = Piece(p.row, p.col, p.color, p.king)
    return new_b

def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Шашки з ботом")
    board = Board()
    selected_piece = None
    valid_moves = {}
    turn = WHITE
    winner = None
    clock = pygame.time.Clock()
    running = True
    while running:
        clock.tick(60)
        board.draw(win)
        if selected_piece and valid_moves:
            for move in valid_moves:
                r, c = move
                x = (c+1) * SQUARE_SIZE + SQUARE_SIZE // 2
                y = (r+1) * SQUARE_SIZE + SQUARE_SIZE // 2
                pygame.draw.circle(win, RED, (x, y), SQUARE_SIZE // 3, 4)

        if winner:
            font_big = pygame.font.SysFont("Arial", 72, bold=True)
            font_small = pygame.font.SysFont("Arial", 36, bold=True)
            color = WHITE if winner == "WHITE" else BLACK
            text = font_big.render(f"{winner} WINS!", True, color)
            shadow = font_big.render(f"{winner} WINS!", True, (50, 50, 50))
            x = WIDTH//2 - text.get_width()//2
            y = HEIGHT//2 - text.get_height()//2
            win.blit(shadow, (x+4, y+4))
            win.blit(text, (x, y))
            sub_text = font_small.render("Press ESC to exit", True, (200, 30, 30))
            win.blit(sub_text, (WIDTH//2 - sub_text.get_width()//2, y + text.get_height() + 20))
            pygame.display.flip()
            continue

        pygame.display.flip()

        if not board.has_pieces_and_moves(turn):
            winner = "WHITE" if turn == BLACK else "BLACK"
            continue

        if turn == BLACK:
            score, best_move = minimax(board, depth=3, alpha=-1e9, beta=1e9,
                                       maximizing=False, start_time=time.time(),
                                       time_limit=2.0, forced_piece=None)
            if best_move:
                piece, move, captured = best_move
                real_piece = board.board[piece.row][piece.col]
                if captured:
                    board.remove_piece(*captured)
                board.move_piece(real_piece, *move)

                if captured:
                    moves, captures = board.get_piece_moves(real_piece)
                    if captures:
                        continue

                turn = WHITE
                continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                row, col = (y // SQUARE_SIZE) - 1, (x // SQUARE_SIZE) - 1
                if row < 0 or col < 0 or row >= ROWS or col >= COLS:
                    continue

                if selected_piece and (row, col) in valid_moves:
                    skipped = valid_moves[(row, col)]
                    if skipped:
                        board.remove_piece(*skipped)
                    board.move_piece(selected_piece, row, col)

                    if skipped:
                        moves, captures = board.get_piece_moves(selected_piece)
                        if captures:
                            valid_moves = captures
                            continue

                    selected_piece = None
                    valid_moves = {}
                    turn = BLACK
                else:
                    piece = board.board[row][col]
                    if piece != 0 and piece.color == WHITE:
                        all_moves, _ = board.get_all_moves(WHITE)
                        if piece in all_moves:
                            selected_piece = piece
                            valid_moves = all_moves[piece]
                        else:
                            selected_piece = None
                            valid_moves = {}

    pygame.quit()

if __name__ == "__main__":
    main()
