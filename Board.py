from Piece import Piece
from typing import Optional

default_pieces = {
    0: Piece((0, 1), (2, 2)),
    1: Piece((0, 0), (2, 1)),
    2: Piece((0, 3), (2, 1)),
    3: Piece((2, 1), (1, 2)),
    4: Piece((3, 0), (2, 1)),
    5: Piece((3, 1), (1, 1)),
    6: Piece((3, 2), (1, 1)),
    7: Piece((4, 1), (1, 1)),
    8: Piece((4, 2), (1, 1)),
    9: Piece((3, 3), (2, 1))
}

class Board(object):
    def __init__(self, dim: tuple[int, int] = (5, 4), pieces: dict[int, Piece] = default_pieces):
        self.dim = dim
        self.state: list[list[Optional[int]]] = [[None for j in range(dim[1])] for i in range(dim[0])]

        for pid, piece in pieces.items():
            for i in range(piece.pos[0], piece.pos[0] + piece.dim[0]):
                for j in range(piece.pos[1], piece.pos[1] + piece.dim[1]):
                    # Update board
                    if self.state[i][j] is None or self.state[i][j] == pid:
                        self.state[i][j] = pid
                    else:
                        raise ValueError(f"Piece conflict: both piece {self.state[i][j]} and piece {pid} are at {(i, j)}")
        
    def simple_print(self):
        for i in range(len(self.state)):
            for j in range(len(self.state[i])):
                print(self.state[i][j] if self.state[i][j] is not None else ' ', end="  ")
            print("\n", end="")


if __name__ == "__main__":
    b = Board()
    b.simple_print()