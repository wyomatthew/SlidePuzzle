import numpy as np, click
from Piece import Piece, X_UNIT, Y_UNIT
from typing import Optional
from queue import PriorityQueue
from itertools import count
from time import perf_counter


default_pieces = {
    1: Piece((0, 1), (2, 2), 1),
    2: Piece((0, 0), (2, 1), 2),
    3: Piece((0, 3), (2, 1), 3),
    4: Piece((2, 1), (1, 2), 4),
    5: Piece((3, 0), (2, 1), 5),
    6: Piece((3, 1), (1, 1), 6),
    7: Piece((3, 2), (1, 1), 7),
    8: Piece((4, 1), (1, 1), 8),
    9: Piece((4, 2), (1, 1), 9),
    10: Piece((3, 3), (2, 1), 10)
}

def int_to_board(rep: int, str_len: int = 60, bits_per_piece: int = 3):
    """Returns the Board object represented by the input integer.
    
    Parameters
    ----------
    rep: int
        Integer representation of board state to be generated
    str_len: int
        Length of binary string representation
    bits_per_piece: int
        Number of bits assigned to each piece"""
    bin_str = (bin(rep)[2:]).zfill(str_len)[::-1]
    raise NotImplementedError()
    # for i in range(0, len(bin_str), bits_per_piece):
    #     if i // bits_per_piece % 4 == 0:
    #         print('\n', end="")

    #     curr_str = bin_str[i:i + bits_per_piece]
    #     if curr_str == '000':
    #         print('   ', end="")
    #     elif curr_str == '001':
    #         print('[] ', end="")
    #     elif curr_str == '010':
    #         print('|| ', end="")
    #     elif curr_str == '110':
    #         print('== ', end="")
    #     elif curr_str == '100':
    #         print('<> ', end="")
    #     else:
    #         print('   ', end="")
    # print('\n')

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
    
    def hashable(self) -> int:
        """Returns a hashable representation of the board state"""
        return self.to_int()

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
        p = dict()

        # Add root (priority, num_moves, unique_counter, board, parent)
        q.put((self.get_goal_dist(), 0, next(cnt), self, None))

        while not q.empty():
            tup = q.get()
            num_moves: int =  tup[1]
            board: Board = tup[3]
            parent: int = tup[4]
            brd_hash = board.hashable()
            if board.hashable() not in p.keys():
                p[brd_hash] = parent
            else:
                continue

            # Check if we've found a goal state
            # board.simple_print()
            if board.is_solved():
                # Trace back solution
                print(f"Made it after looking at {len(p)} board states!")
                out = list()
                curr = brd_hash
                while brd_hash in p.keys() and curr is not None:
                    out.append(curr)
                    curr = p[curr]
                
                return out[::-1]
            
            # Look at all children
            for next_board, pid, move in board.get_successors():
                # add child
                if next_board.hashable() not in p.keys():
                    q.put((num_moves + 1 + next_board.get_goal_dist(), num_moves, next(cnt), next_board, brd_hash))
        
        return None

    def to_int(self) -> int:
        """Returns representation of current board state as 64 bit integer. Each
        square on the board is given 2 bits encoded as the following:
        0 = empty (00)
        1 = small square (01)
        2 = vertical rectangle (10)
        3 = horizontal rectangle (11)
        4 = big square"""
        bit_str = np.zeros(self.dim[0] * self.dim[1] * 3, int)

        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                # Get range of indices
                lo = (i * self.dim[1] + j) * 3
                hi = lo + 3

                piece_dim = self.pieces.get(self.state[i, j], None)
                if piece_dim is not None:
                    piece_dim = piece_dim.dim
                
                if piece_dim is None:
                    bit_str[lo:hi] = 0
                elif piece_dim == (1, 1):
                    bit_str[lo:hi] = (0, 0, 1)
                elif piece_dim == (2, 1):
                    bit_str[lo:hi] = (0, 1, 0)
                elif piece_dim == (1, 2):
                    bit_str[lo:hi] = (0, 1, 1)
                elif piece_dim ==  (2, 2):
                    bit_str[lo:hi] = (1, 0, 0)
                else:
                    raise ValueError(f"Found piece with illegal dimensions: {piece_dim}")
        
        return int(bit_str.dot(2**np.arange(bit_str.size)[::-1]))

    @staticmethod
    def print_int(rep: int, str_len: int = 60, bits_per_piece: int = 3):
        """Given an integer representation of the board, prints out the board
        state.
        
        Parameters
        ----------
        rep: int
            Integer encoding binary representation of board
        str_len: int
            Length of binary string encoding
        bits_per_piece: int
            Number of bits each piece gets"""
        bin_str = (bin(rep)[2:]).zfill(str_len)[::-1]
        for i in range(0, len(bin_str), bits_per_piece):
            if i // bits_per_piece % 4 == 0:
                print('\n', end="")

            curr_str = bin_str[i:i + bits_per_piece]
            if curr_str == '000':
                print('   ', end="")
            elif curr_str == '001':
                print('[] ', end="")
            elif curr_str == '010':
                print('|| ', end="")
            elif curr_str == '110':
                print('== ', end="")
            elif curr_str == '100':
                print('<> ', end="")
            else:
                print('   ', end="")
        print('\n')

    def simple_print(self):
        wid = 18
        print("-" * wid)
        for i in range(len(self.state)):
            print("|", end="")
            for j in range(len(self.state[i])):
                print(f"{self.state[i, j]:2d}" if self.state[i, j] > 0 else '  ', end="  ")
            print("|\n", end="")
        print("-" * wid)

    def click_print(self):
        click.clear()
        for board_row in range(self.dim[0]):
            # Print current line
            for term_row in range(Y_UNIT):
                # Current line of the current row
                board_col = 0
                while board_col < self.dim[1]:
                    if self.state[board_row, board_col] > 0:
                        piece = self.pieces[self.state[board_row, board_col]]
                        line_num = (board_row - piece.pos[0]) * Y_UNIT + term_row

                        click.echo(click.style(piece.str_list[line_num], fg=piece.col), nl=False)
                        board_col += piece.dim[1]
                    else:
                        # No piece, print out spaces
                        click.echo(" " * X_UNIT, nl=False)
                        board_col += 1
                print("\n", end="")


if __name__ == "__main__":
    b = Board()
    b.click_print()
    input()
    b.perform_move(2, (1, 0))
    b.click_print()
    # print(f"Solving!")
    # t_0 = perf_counter()
    # sol = b.solve()
    # print(f"Solved in {perf_counter() - t_0}s!")
    # with open(f"sol.txt", "w") as fp:
    #     for bin_rep in sol:
    #         Board.print_int(bin_rep)
    #         input()
    #         fp.write(f"{bin_rep}\n")
    