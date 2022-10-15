# Setting Sun Puzzle
This project provides an interactive user interface for playing and solving the
Setting Sun puzzle. The puzzle itself features a collection of differently sized
blocks with the object being to take the biggest block, the sun, to the bottom
of the puzzle frame. Read more and see a standard visualization for the puzzle
<a href='https://smallpond.ca/jim/misc/settingSun/solution.html'>here</a>.

## Installation
To install, begin by cloning the repo. Then, install the dependencies featured in `env.yml`.

With conda:
```
conda env create -f env.yml
```

## Usage
Two main usages are supported: interactively attempting the puzzle and calling the built-in puzzle solver.

By default, executing `Sunset.py` without any other options opens the board interactively, prompting the user to enter moves and solve the puzzle themselves:

With conda:
```
conda run -n SettingSun python Sunset.py
```
With your favorite python interpreter:
```
path/to/interpreter Sunset.py
```

If passed the `--solution, -s` option, then the program instead solves the puzzle from the initial state and offers a walkthrough move-by-move of the solution:

With conda:
```
conda run -n SettingSun python Sunset.py --solution
```
With your favorite python interpreter:
```
path/to/interpreter Sunset.py --solution
```

At any point, the user can use the `--help` option for a reminder:
```
$ conda run -n SettingSun Sunset.py --help
Usage: Sunset.py [OPTIONS]

Options:
  -s, --solution  Solves and offers a walkthrough of the puzzle as opposed to
                  allowing to play with it interactively
  --help          Show this message and exit.
```
## Architecture
The program is divided into 3 modules:

### Sunset.py
Module containing all direct interaction with the user and the program's main method. It instantiates objects and makes calls to functions in `Board.py`

### Board.py
Holds the Class representation of any board and the logic to solve the board state. Represents any board using two data structures, one 2D array of integer values (0 representing empty space, any other number representing the piece ID of the piece occupying that square) and one dictionary mapping from piece IDs to the Piece object as provided by `Piece.py`

### Piece.py
Basic dataclass for representing a single piece. Stores the piece's dimensions, position, optional ID, string representation, and any color that should be applied when printing.

## Solution AI
The program solves any puzzle state via a standard implementation of $A^*$ search. The search is performed by interpreting any board state as a node $v$ and adding an edge $(v, u)$ if there is a legal move from board state $v$ that results in board state $u$. In the interest of optimization, visited board states are hashed to a dictionary during the search and not revisited once they are removed from the priority queue.

To efficiently hash any board state, the program can transform any board state to a unique 64-bit integer. This is accomplished by assigning each cell a unique 3 bits in the string, where the value of those 3 bits identify whether or not a piece is in that cell and, if so, the dimensions of the piece:

- 000 -> Empty
- 001 -> 1x1
- 010 -> 2x1
- 011 -> 1x2
- 100 -> 2x2

Since $A^*$ requires an admissible heuristic that **under-estimates** the true path cost from any state to a goal state, the program defines its heuristic function $h(n)$ on any state $n$ to be the sum of the number of moves to get the 2x2 piece to the goal position and the number of pieces occupying the 4 goal squares that the 2x2 piece must get to. We guarantee this to be admissible since it will clearly take at least as many moves as it will take to get the 2x2 piece to the goal position without any constraints, and each piece occupying those cells must be moved at least once to get out of the way.
