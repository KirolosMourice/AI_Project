import copy
import sys
import pygame
import heapq
import random
import numpy as np

from constant import *

# --- PYGAME SETUP ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TIC TAC TOE AI")
screen.fill(BG_COLOR)

# --- COLORS ---
FRAME_COLOR = (72, 61, 139)    # Dark Slate Blue for the frame
BG_COLOR = (240, 248, 255)     # Alice Blue background
LINE_COLOR = (123, 104, 238)   # Medium Slate Blue for grid lines
CIRC_COLOR = (250, 128, 114)   # Salmon for circles (O)
CROSS_COLOR = (0, 191, 255)    # Deep Sky Blue for crosses (X)

# --- CLASSES ---
class Board:
    def __init__(self):
        self.squares = np.zeros((ROWS, COLS))
        self.marked_sqrs = 0

    def final_state(self, show=False):
        """
        Checks the game's final state.
        Returns:
            0 if no winner yet
            1 if Player 1 wins
            2 if Player 2 wins
        """
        # Vertical wins
        for col in range(COLS):
            if self.squares[0][col] == self.squares[1][col] == self.squares[2][col] != 0:
                if show:
                    color = CIRC_COLOR if self.squares[0][col] == 2 else CROSS_COLOR
                    iPos = (col * SQSIZE + SQSIZE // 2, 20)
                    fPos = (col * SQSIZE + SQSIZE // 2, HEIGHT - 20)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[0][col]

        # Horizontal wins
        for row in range(ROWS):
            if self.squares[row][0] == self.squares[row][1] == self.squares[row][2] != 0:
                if show:
                    color = CIRC_COLOR if self.squares[row][0] == 2 else CROSS_COLOR
                    iPos = (20, row * SQSIZE + SQSIZE // 2)
                    fPos = (WIDTH - 20, row * SQSIZE + SQSIZE // 2)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[row][0]

        # Descending diagonal
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] != 0:
            if show:
                color = CIRC_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                iPos = (20, 20)
                fPos = (WIDTH - 20, HEIGHT - 20)
                pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDTH)
            return self.squares[1][1]

        # Ascending diagonal
        if self.squares[2][0] == self.squares[1][1] == self.squares[0][2] != 0:
            if show:
                color = CIRC_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                iPos = (20, HEIGHT - 20)
                fPos = (WIDTH - 20, 20)
                pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDTH)
            return self.squares[1][1]

        return 0  # No winner yet

    def mark_sqr(self, row, col, player):
        self.squares[row][col] = player
        self.marked_sqrs += 1

    def empty_sqr(self, row, col):
        return self.squares[row][col] == 0

    def get_empty_sqrs(self):
        return [(row, col) for row in range(ROWS) for col in range(COLS) if self.empty_sqr(row, col)]

    def isfull(self):
        return self.marked_sqrs == 9

    def isempty(self):
        return self.marked_sqrs == 0


class AI:
    def __init__(self, level=1, player=2):
        self.level = level
        self.player = player

    def bfs(self, board):
        return board.get_empty_sqrs()[0]

    def dfs(self, board):
        return board.get_empty_sqrs()[-1]
    
    def ucs(self, board):
        pq = []
        empty_sqrs = board.get_empty_sqrs()
        for (row, col) in empty_sqrs:
            cost = self.evaluate_cost(board, row, col)
            heapq.heappush(pq, (cost, (row, col)))
            print(f"Evaluating move {(row, col)}: cost = {cost}")  # Debugging
        _, best_move = heapq.heappop(pq)
        print(f"UCS chose move {best_move} with lowest cost")  # Debugging
        return best_move


    def evaluate_cost(self, board, row, col):
         """
         Assign a cost to the given move. Lower costs are better.
         - Winning moves have the highest priority (cost = 0).
         - Blocking the opponent from winning is the next priority (cost = 1).
         - Strategic moves (e.g., center square) have moderate priority (cost = 2).
         - Other moves have higher costs.
         """
         temp_board = copy.deepcopy(board)

        # Check if the move wins the game
         temp_board.mark_sqr(row, col, self.player)
         if temp_board.final_state() == self.player:
            print(f"Evaluating cost for move ({row}, {col}): 0 (winning move)")
            return 0  # Winning move

        # Check if the move blocks the opponent's win
         opponent = 1 if self.player == 2 else 2
         temp_board = copy.deepcopy(board)  # Reset the board
         temp_board.mark_sqr(row, col, opponent)
         if temp_board.final_state() == opponent:
            print(f"Evaluating cost for move ({row}, {col}): 1 (blocking opponent's winning move)")
            return 1  # Blocking move

        # Center square preference
         if board.isempty() and (row, col) == (1, 1):
            print(f"Evaluating cost for move ({row}, {col}): 2 (center square preference)")
            return 2  # Center is strategic if the board is empty

        # All other moves
         print(f"Evaluating cost for move ({row}, {col}): 3 (neutral move)")
         return 3  # Neutral moves



    def rnd(self, board):
        return random.choice(board.get_empty_sqrs())

    def eval(self, main_board):
        if self.mode == "bfs":
            move = self.bfs(main_board)
        elif self.mode == "dfs":
            move = self.dfs(main_board)
        elif self.mode == "ucs":
            move = self.ucs(main_board)
        else:
            move = self.rnd(main_board)

        print(f"AI ({self.mode}) chose square {move}")
        return move

    

    def check_winner(self, board, player):
        """Check if the given player wins with the current board state."""
        # Vertical, horizontal, and diagonal checks
        for col in range(COLS):
            if board[0][col] == board[1][col] == board[2][col] == player:
                return True

        for row in range(ROWS):
            if board[row][0] == board[row][1] == board[row][2] == player:
                return True

        if board[0][0] == board[1][1] == board[2][2] == player:
            return True
        if board[2][0] == board[1][1] == board[0][2] == player:
            return True

        return False

    def is_advancing_win(self, board, player):
        """Check if the AI is advancing toward a win."""
        # Check if any row, column, or diagonal is almost complete for the player
        for col in range(COLS):
            if board[0][col] == board[1][col] == player and board[2][col] == 0:
                return True
            if board[1][col] == board[2][col] == player and board[0][col] == 0:
                return True

        for row in range(ROWS):
            if board[row][0] == board[row][1] == player and board[row][2] == 0:
                return True
            if board[row][1] == board[row][2] == player and board[row][0] == 0:
                return True

        if board[0][0] == board[1][1] == player and board[2][2] == 0:
            return True
        if board[1][1] == board[2][2] == player and board[0][0] == 0:
            return True

        if board[2][0] == board[1][1] == player and board[0][2] == 0:
            return True
        if board[1][1] == board[0][2] == player and board[2][0] == 0:
            return True

        return False


class Game:
    
    def __init__(self, mode):
        self.board = Board()
        self.ai = AI(level=1, player=2)
        self.ai.mode = mode  # Ensure the correct mode is set
        self.player = 1
        self.running = True
        self.show_lines()


    def show_lines(self):
        screen.fill(BG_COLOR)

        # Draw frame
        frame_margin = 20
        pygame.draw.rect(screen, FRAME_COLOR, 
                         (frame_margin, frame_margin, WIDTH - 2 * frame_margin, HEIGHT - 2 * frame_margin), 10)

        # Draw grid lines
        for i in range(1, ROWS):
            pygame.draw.line(screen, LINE_COLOR, 
                             (frame_margin, i * SQSIZE + frame_margin), 
                             (WIDTH - frame_margin, i * SQSIZE + frame_margin), LINE_WIDTH)
            pygame.draw.line(screen, LINE_COLOR, 
                             (i * SQSIZE + frame_margin, frame_margin), 
                             (i * SQSIZE + frame_margin, HEIGHT - frame_margin), LINE_WIDTH)

    def draw_fig(self, row, col):
        if self.player == 1:  # Cross (X)
            start_desc = (col * SQSIZE + OFFSET, row * SQSIZE + OFFSET)
            end_desc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            pygame.draw.line(screen, CROSS_COLOR, start_desc, end_desc, CROSS_WIDTH)
            start_asc = (col * SQSIZE + OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            end_asc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + OFFSET)
            pygame.draw.line(screen, CROSS_COLOR, start_asc, end_asc, CROSS_WIDTH)
        elif self.player == 2:  # Circle (O)
            center = (col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2)
            pygame.draw.circle(screen, CIRC_COLOR, center, RADIUS, CIRC_WIDTH)

    def make_move(self, row, col):
        self.board.mark_sqr(row, col, self.player)
        self.draw_fig(row, col)
        self.player = self.player % 2 + 1

    def isover(self):
        return self.board.final_state(show=True) != 0 or self.board.isfull()

    def reset(self):
        self.__init__(self.ai.mode)


def main():
    mode = "bfs"  # AI mode (can be bfs, dfs, ucs, or rnd)
    game = Game(mode)

    while game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.isover():
                    game.reset()
                else:
                    x, y = event.pos
                    row = (y - 20) // SQSIZE
                    col = (x - 20) // SQSIZE

                    if game.board.empty_sqr(row, col):
                        game.make_move(row, col)

                    if game.isover():
                        winner = game.board.final_state()
                        print(f"Game Over! Player {winner} wins.")
                        pygame.time.wait(2000)

        if game.player == 2 and not game.isover():
            row, col = game.ai.eval(game.board)
            game.make_move(row, col)

        pygame.display.update()

    pygame.quit()
    sys.exit()

def main():
    # Terminal-based mode selection for AI
    print("Choose AI mode:")
    print("BFS: Enter 'b'")
    print("DFS: Enter 'd'")
    print("UCS: Enter 'u'")
    mode = input("Your choice: ").strip().lower()
    while mode not in ['b', 'd', 'u']:
        mode = input("Invalid choice! Enter 'b', 'd', or 'u': ").strip().lower()

    mode_map = {'b': "bfs", 'd': "dfs", 'u': "ucs"}
    selected_mode = mode_map[mode]
    print(f"You selected {selected_mode.upper()}. Starting game...")

    # Option to choose who starts first
    print("\nWho should start the game?")
    print("Human: Enter 'h'")
    print("AI: Enter 'a'")
    starter = input("Your choice: ").strip().lower()
    while starter not in ['h', 'a']:
        starter = input("Invalid choice! Enter 'h' or 'a': ").strip().lower()

    human_starts = starter == 'h'
    print(f"{'Human' if human_starts else 'AI'} will start the game.")

    # Initialize game with the selected AI mode
    game = Game(mode=selected_mode)

    # Set the starting player
    if not human_starts:
        game.player = game.ai.player

    # Main game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and game.running and game.player == 1:
                mouseX, mouseY = event.pos
                clicked_row = mouseY // SQSIZE
                clicked_col = mouseX // SQSIZE

                if game.board.empty_sqr(clicked_row, clicked_col):
                    game.make_move(clicked_row, clicked_col)

                    if game.isover():
                        game.running = False

        if game.player == game.ai.player and game.running:
            pygame.display.update()
            row, col = game.ai.eval(game.board)
            game.make_move(row, col)

            if game.isover():
                game.running = False

        pygame.display.update()

if __name__ == "__main__":
    main()

        
