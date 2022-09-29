import numpy as np
from Piece import Piece
from typing import Optional
from queue import PriorityQueue
from itertools import count


default_pieces = {
    1: Piece((0, 1), (2, 2)),
    2: Piece((0, 0), (2, 1)),
    3: Piece((0, 3), (2, 1)),
    4: Piece((2, 1), (1, 2)),
    5: Piece((3, 0), (2, 1)),
    6: Piece((3, 1), (1, 1)),
    7: Piece((3, 2), (1, 1)),
    8: Piece((4, 1), (1, 1)),
    9: Piece((4, 2), (1, 1)),
    10: Piece((3, 3), (2, 1))
}

class Board(object):
    def __init__(self, dim: tuple[int, int] = (5, 4), 
            pieces: dict[int, Piece] = default_pieces, 
            goal_piece: Optional[int] = 1, 
            goal_pos: Optional[tuple[int, int]] = (3, 1)):
        self.dim = dim
        self.state: list[list[Optional[int]]] = np.zeros(dim, dtype=int)
        self.pieces = pieces
        self.goal_piece = goal_piece
        self.goal_pos = goal_pos

        for pid, piece in pieces.items():
            for i in range(piece.pos[0], piece.pos[0] + piece.dim[0]):
                for j in range(piece.pos[1], piece.pos[1] + piece.dim[1]):
                    # Update board
                    if self.state[i, j] == 0 or self.state[i, j] == pid:
                        self.state[i][j] = pid
                    else:
                        raise ValueError(f"Piece conflict: both piece {self.state[i][j]} and piece {pid} are at {(i, j)}")
    
    def get_coords(self, pid: int) -> tuple[tuple[int, int], tuple[int, int]]:
        """Returns the start and end row, col coordinates of the input piece.
        
        Parameters
        ----------
        pid: int
            Unique identifier for piece. Must be a key in `self.pieces`."""
        piece = self.pieces[pid]
        x_coords = (piece.pos[0], piece.pos[0] + piece.dim[0])
        y_coords = (piece.pos[1], piece.pos[1] + piece.dim[1])
        return x_coords, y_coords

    def get_squares(self, pid: int) -> np.ndarray:
        """Returns the subarray representing the squares occupied by the input
        piece.
        
        Parameters
        ----------
        pid: int
            Unique identifier for piece. Must be a key in `self.pieces`."""
        coords = self.get_coords(pid)
        return self.state[coords[0][0]:coords[0][1],coords[1][0]:coords[1][1]]

    def get_piece_moves(self, pid: int):
        """Yields all legal moves the input piece can make in the form of (x, y)
        tuples signifying the destination.
        
        Parameters
        ----------
        pid: int
            Unique identifier for piece. Must be a key in `self.pieces`.
        """
        # Get the coords of the piece
        (start_row, end_row), (start_col, end_col) = self.get_coords(pid)

        # Try moving up
        if start_row > 0 and np.all(np.roll(self.state, 1, axis=0)[start_row, start_col:end_col] == 0):
            yield (start_row - 1, start_col)

        # Try moving down
        if end_row < self.dim[0] and np.all(np.roll(self.state, -1, axis=0)[end_row - 1, start_col:end_col] == 0):
            yield (start_row + 1, start_col)
        
        # Try moving left
        if start_col > 0 and np.all(np.roll(self.state, 1, axis=1)[start_row:end_row, start_col] == 0):
            yield (start_row, start_col - 1)
        
        # Try moving right
        if end_col < self.dim[1] and np.all(np.roll(self.state, -1, axis=1)[start_row:end_row, end_col - 1] == 0):
            yield (start_row, start_col + 1)

    def perform_move(self, pid: int, tgt: tuple[int, int]):
        """Modifies the board state in place to reflect the input move.
        
        Parameters
        ----------
        pid: int
            Unique identifier for piece to be moved
        tgt: tuple[int, int]
            Tuple identfying (row, col) to move input piece to"""
        # Clear current squares
        (start_row, end_row), (start_col, end_col) = self.get_coords(pid)
        self.state[start_row:end_row,start_col:end_col] = 0

        # Put piece in its new location
        piece = self.pieces[pid]
        piece.pos = tgt
        self.state[tgt[0]:tgt[0]+piece.dim[0],tgt[1]:tgt[1]+piece.dim[1]] = pid
        
    def copy(self):
        """Makes a deep copy of the board instance"""
        new_pieces = dict()
        for pid, piece in self.pieces.items():
            new_pieces[pid] = Piece(piece.pos, piece.dim)
        
        return Board(self.dim, new_pieces, self.goal_piece, self.goal_pos)

    def get_successors(self):
        """Yields all continuing board states from the current state in the form
        of (board, pid, move) tuples."""
        for pid in self.pieces.keys():
            for tgt in self.get_piece_moves(pid):
                new_board = self.copy()
                new_board.perform_move(pid, tgt)
                yield (new_board, pid, tgt)

    def is_solved(self):
        """Returns whether or not the current board instance is solved."""
        return self.pieces[self.goal_piece].pos == self.goal_pos
    
    def tuplize(self) -> tuple[tuple[int]]:
        """Returns a tuple representation of the board state"""
        return tuple([self.pieces[self.state[row,col]].dim if self.state[row,col] != 0 else 0 for row in range(self.dim[0]) for col in range(self.dim[1])])

    def get_goal_dist(self) -> int:
        """Returns the heuristic distance to the goal state from the current
        state."""
        # Return sum of number of moves to get goal piece to goal pos + num blocking pieces
        goal_piece = self.pieces[self.goal_piece]
        start_row = self.goal_pos[0]
        end_row = self.goal_pos[0] + goal_piece.dim[0]
        start_col = self.goal_pos[1]
        end_col = self.goal_pos[1] + goal_piece.dim[1]
        goal_squares = self.state[start_row:end_row,start_col:end_col]
        return np.sum(np.abs(np.array(goal_piece.pos) - np.array((start_row, start_col)))) + np.count_nonzero(np.unique(goal_squares))

    def solve(self) -> list[tuple[int, tuple[int, int]]]:
        """Returns a solution to the current puzzle in the form of a list of
        (pid, tgt) tuples."""
        q = PriorityQueue()
        cnt = count()
        seen = set()

        # Add root (priority, unique_counter, board, moves)
        q.put((self.get_goal_dist(), next(cnt), self, list()))

        while not q.empty():
            tup = q.get()
            board: Board = tup[2]
            moves: list[tuple[int, tuple[int, int]]] = tup[3]
            seen.add(board.tuplize())

            # Check if we've found a goal state
            # board.simple_print()
            if board.is_solved():
                return moves
            
            # Look at all children
            for next_board, pid, move in board.get_successors():
                # add child
                if next_board.tuplize() not in seen:
                    q.put((len(moves) + 1 + next_board.get_goal_dist(), next(cnt), next_board, moves + [(pid, move)]))
        
        return None


    def simple_print(self):
        wid = 18
        print("-" * wid)
        for i in range(len(self.state)):
            print("|", end="")
            for j in range(len(self.state[i])):
                print(f"{self.state[i, j]:2d}" if self.state[i, j] > 0 else '  ', end="  ")
            print("|\n", end="")
        print("-" * wid)


if __name__ == "__main__":
    b = Board()
    b.simple_print()
    # piece = 4
    # print(f"Piece {piece} coords: {b.get_coords(piece)}")

    # print(list(b.get_piece_moves(piece)))

    # b.perform_move(4, (2, 0))

    # b.simple_print()
    # print(b.pieces[piece])

    # print(b.get_goal_dist())
    # print(b.tuplize())

    print(f"Solving!")
    sol = b.solve()
    print(f"Solution got!\n{sol}")
    