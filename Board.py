from Piece import Piece

default_pieces = {
    0: Piece((0, 1), (2, 2)),
    1: Piece((0, 0), (2, 1)),
    2: Piece((0, 3), (2, 1)),
    3: Piece((2, 1), (1, 2)),
    4: Piece((3, 0), (2, 1)),
    5: Piece((3, 1), (1, 1)),
    6: Piece((3, 2), (1, 1)),
    7: Piece((4, 1), (1, 1)),
    8: Piece((4, 2), (1, 2)),
    9: Piece((3, 3), (2, 1))
}

class Board(object):
    def __init__(self, dim: tuple[int, int] = (5, 4), pieces: dict[int, Piece] = default_pieces):
        self.dim = dim
        self.board = [[None for j in range(dim[1])] for i in range(dim[0])]

        for pid, piece in pieces.items():
            for i in range(piece.pos[0], piece.pos[0] + piece.dim[0]):
                for j in range(piece.pos[1], piece.pos[1] + piece.dim[1]):
                    # Update board
                    if self.board[i][j] is None or self.board[i][j] == pid:
                        self.board[i][j] = pid
                    raise ValueError(f"Piece conflict: both piece {self.board[i][j]} and piece {pid} are at {(i, j)}")
        
    def simple_print(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                print(self.board[i][j] if self.board[i][j] is not None else 'X', end="")
            print("\n", end="")


if __name__ == "__main__":
    b = Board()
    b.simple_print()