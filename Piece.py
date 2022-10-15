import click
from dataclasses import dataclass, field

color_map = {
    (1, 1): (0, 0, 255),
    (2, 1): (255, 255, 0),
    (1, 2): (0, 255, 0),
    (2, 2): (255, 0, 0)
}

str_map = {
    (1, 1): 
"""
 ___
|   |
|___|
""", 
    (2, 1):
"""
 ___ 
|   |
|   |
|   |
|   |
|___|
""",
    (1, 2):
"""
 ________
|        |
|________|
""",
    (2, 2):
"""
 ________
|        |
|        |
|        |
|        |
|________|
"""
}

X_UNIT = 5 # Width of a (1 x 1) piece in characters
Y_UNIT = 3 # Height of a (1 x 1) piece in characters

@dataclass
class Piece(object):
    pos: tuple[int, int]
    dim: tuple[int, int]
    col: tuple[int, int, int] = field(default=None, init=False, compare=False)

    def __post_init__(self):
        if self.dim[0] < 1 or self.dim[1] < 1:
            raise ValueError(f"All dimensions must be at least 1, received {self.dim}")
        self.col = color_map.get(self.dim, None)
        self.str_list = list()

        char_height = self.dim[0] * 3 # Height of print out of object
        for i in range(self.dim[0] * 3):
            num_middle = self.dim[1] * 5 - 2 # Number of characters between left and right edges
            if i == 0: # Handle case we are first line
                line_str = f" {'_' * num_middle} "
            elif i == char_height - 1: # Handle case we are last line
                line_str = f"|{'_' * num_middle}|"
            else:
                line_str = f"|{' ' * num_middle}|"
            self.str_list.append(line_str)
        
        self.term_dim = (len(self.str_list), len(self.str_list[0]))

if __name__ == '__main__':
    for dim in [(1, 1), (2, 1), (1, 2), (2, 2)]:
        print(f"Checking {dim}:")
        Piece((0, 0), dim)