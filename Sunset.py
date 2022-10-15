import click
from typing import Optional
from Board import Board

@click.command()
def hello():
    click.echo(click.style("Hello world!", fg=(255, 0, 0), blink=True))

move_map = {
    'w': (-1, 0),
    'a': (0, -1),
    's': (1, 0),
    'd': (0, 1)
}

def take_user_move(b: Board) -> Optional[int]:
    """Prompts user to make a move and performs it on the input board. Returns
    the pid of the piece moved if a move was successfully made."""
    pid = click.prompt(f"Select a piece to move: ", type=int)
    if pid not in b.pieces.keys():
        raise ValueError(f"Piece must exist on the board! Received {pid}")
    p = b.pieces[pid]

    # Get direction
    click.echo(f"Please enter a direction to move")
    dir_key = click.getchar()
    if dir_key not in move_map.keys():
        raise ValueError(f"Movement direction must be one of {set(move_map.keys())}! Received {dir_key}")
    diff = move_map[dir_key]
    new_pos = (p.pos[0] + diff[0], p.pos[1] + diff[1])

    # Get all legal moves
    if (pid, new_pos) not in [(next_pid, next_dir) for _, next_pid, next_dir in b.get_successors()]:
        raise ValueError(f"Movement is illegal! Received {pid} to {new_pos}")

    b.perform_move(pid, new_pos)
    return pid

if __name__ == '__main__':
    # Generate board
    b = Board()

    # Enter main loop
    err_str: Optional[str] = None
    while not b.is_solved():
        b.click_print(clear=True)
        if err_str is not None:
            print(err_str)

        # Prompt user
        try:
            last_pid = take_user_move(b)
        except ValueError as err:
            err_str = str(err)