from dataclasses import dataclass

@dataclass
class Piece(object):
    pos: tuple[int, int]
    dim: tuple[int, int]

    