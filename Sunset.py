import click
from typing import Optional
from Board import Board, int_to_board

move_map = {
    'w': (-1, 0),
    'a': (0, -1),
    's': (1, 0),
    'd': (0, 1)
}

def take_user_move(b: Board) -> Optional[int]:
    """Prompts user to make a move and performs it on the input board. Returns
    the pid of the piece moved if a move was successfully made."""
    pid = click.prompt(f"Type 's' to let the computer solve or input a piece ID to move")
    if pid == 's':
        solve_board(b)
    pid = int(pid)

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

def handle_user_play(b: Board):
    """Handles the default behavior of allowing the user to play on the board."""
    # Enter main loop
    err_str: Optional[str] = None
    while not b.is_solved():
        b.click_print(clear=True)
        if err_str is not None:
            print(err_str)
            err_str = None

        # Prompt user
        try:
            last_pid = take_user_move(b)
        except ValueError as err:
            err_str = str(err)
    b.click_print(clear=True)
    click.echo(click.style("Congratulations! You've solved it!", (0, 255, 0)))
    exit(0)

def solve_board(b: Board):
    """Solves the input board for the user, provides solution analytics, and
    offers to provide a step-by-step walkthrough of the solution.
    
    Parameters
    ----------
    b: Board
        Board to be solved"""
    click.echo("Solving board...")
    sol, num_boards, time = b.solve()
    
    if sol is not None:
        click.echo(f"Managed to find a length {len(sol)} solution to the puzzle in {time:.2f}s after looking at {num_boards} board states!")
        view_sequence = click.confirm("Would you like to visualize the sequence of moves?")
        if view_sequence:
            for board_int in sol:
                curr_b = int_to_board(board_int)
                curr_b.click_print(clear=True)
                click.echo(f"Press 'q' to quit, 'u' to take it from here, or spacebar to go to next: ", nl=True)
                char = click.getchar(True)
                if char == 'q':
                    print("\n", end="")
                    break
                elif char == 'u':
                    handle_user_play(int_to_board(board_int, assign_pids=True))
    else:
        click.echo("No solution could be found!")
    exit(0)


@click.command()
@click.option("-s", "--solution", is_flag=True, help="Solves and offers \
a walkthrough of the puzzle as opposed to allowing to play with it interactively")
def main(solution):
    b = Board()
    if solution:
        # Solve problem
        solve_board(b)
    else:
        handle_user_play(b)


if __name__ == "__main__":
    main()