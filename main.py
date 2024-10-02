import numpy as np
import hashlib
from numba import jit
from sympy import prevprime
from GraphTsetlinMachine.graphs import Graphs


class HexGame:
    def __init__(self, size):
        self.size = size
        self.graph = Graphs(number_of_graphs=1, symbol_names=["Player1", "Player2"])
        self.graph.set_number_of_graph_nodes(0, size * size)  # One node per cell in the grid
        self.graph.prepare_node_configuration()
        self.current_player = 0  # Player 1 starts

        # Initialize the board
        self.board = np.full((size, size), -1)  # -1 represents empty cells
        self.graph.prepare_edge_configuration()

    def get_current_player_symbol(self):
        return "Player1" if self.current_player == 0 else "Player2"

    def make_move(self, row, col):
        if self.board[row, col] != -1:
            print("Invalid move! Cell already occupied.")
            return False

        # Place the player's marker
        self.board[row, col] = self.current_player
        node_name = f"{row}_{col}"
        self.graph.add_graph_node(0, node_name, 0)  # No edges in this implementation
        self.graph.add_graph_node_feature(0, node_name, self.get_current_player_symbol())

        # Check for win condition
        if self.check_winner(row, col):
            print(f"{self.get_current_player_symbol()} wins!")
            return True

        # Switch player
        self.current_player = 1 - self.current_player
        return True

    def check_winner(self, row, col):
        # Implement a simple BFS or DFS to check if there's a winning path
        visited = set()
        target_row = self.size - 1 if self.current_player == 0 else self.size - 1

        def dfs(r, c):
            if (r, c) in visited or r < 0 or r >= self.size or c < 0 or c >= self.size:
                return False
            if self.board[r, c] != self.current_player:
                return False

            visited.add((r, c))

            # Check if the player has reached the last row
            if self.current_player == 0 and r == target_row:
                return True
            if self.current_player == 1 and c == target_row:
                return True

            # Explore neighbors
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]:
                if dfs(r + dr, c + dc):
                    return True

            return False

        return dfs(row, col)

    def display_board(self):
        for row in self.board:
            print(" ".join(["." if x == -1 else "X" if x == 0 else "O" for x in row]))


# Example of how to use the HexGame class
if __name__ == "__main__":
    game = HexGame(size=5)

    game.display_board()  # Display initial empty board
    game.make_move(0, 0)  # Player 1 moves
    game.display_board()
    game.make_move(0, 1)  # Player 2 moves
    game.display_board()
    game.make_move(1, 1)  # Player 1 moves
    game.display_board()
    game.make_move(1, 2)  # Player 2 moves
    game.display_board()
    game.make_move(2, 2)  # Player 1 moves
    game.display_board()
    game.make_move(3, 2)  # Player 2 moves
    game.display_board()
    game.make_move(3, 3)  # Player 1 moves
    game.display_board()
    # Continue with moves until a player wins
