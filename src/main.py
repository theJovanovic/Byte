import pygame
from typing import Tuple

from display.gui import GUI
from board.board import Board
from utils.movement import get_clicked_tile_position
import utils.colors as colors


def print_end_game(
        board: Board
    ) -> bool:
    winner = 'White' if board.white_points > board.black_points else 'Black'
    print(f'{winner} won!')


def process_move(
        board: Board, 
        x: int, 
        y: int, 
        tile_size: int
    ) -> bool:
    row, column = get_clicked_tile_position(x, y, tile_size)
    is_winning_move = board.move_stack(row, column)
    if is_winning_move:
        print_end_game(board)
        return False
    return True
    

def process_ai_move(
        board: Board
    ) -> bool:
    is_winning_move = board.make_ai_move()
    if is_winning_move:
        print_end_game(board)
        return False
    return True


def handle_mouse_button(
        event: pygame.event.Event, 
        board: Board, 
        tile_size: int, 
        running: bool
    ) -> bool:
    x, y = event.pos

    if event.button == 1:
        board.change_clicked_stack_status(x, y)

    elif event.button == 2:
        return process_ai_move(board)
    
    elif event.button == 3:
        return process_move(board, x, y, tile_size)
    
    return running


def process_events(
        board: Board, 
        gui: GUI, 
        running: bool, 
        tile_size: int
    ) -> bool:
    is_still_running = running
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            is_still_running = handle_mouse_button(event, board, tile_size, running)
    gui.draw_board(board)
    gui.update_caption(board.get_current_player_color())
    pygame.display.update()
    return is_still_running


def setup_game(
        screen: pygame.Surface, 
        board_size: int, 
        current_player: Tuple[int, int, int]
    ) -> Tuple[GUI, Board]:
    gui = GUI(screen)
    tile_size = screen.get_height() // board_size
    board = Board(board_size, tile_size, current_player)
    board.initialize_board()
    return gui, board


def start_game(
        board_size: int, 
        current_player: Tuple[int, int, int]
    ) -> None:
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    running = True
    gui, board = setup_game(screen, board_size, current_player)
    tile_size = screen.get_height() // board_size
    while running:
        running = process_events(board, gui, running, tile_size)
    pygame.quit()


if __name__ == '__main__':
    players = {}

    # board_size = int(input('Input board size [8,10,16]: '))
    board_size = 8
    while board_size not in [8, 10, 16]:
        print('Wrong input. Try again!')
        board_size = int(input('Input board size: '))

    # first_color = input('What color is to make the first move [w/b]: ')
    first_color = 'w'
    while first_color not in ['w', 'W', 'b', 'B']:
        print('Wrong input. Try again!')
        first_color = input('Who is to make the first move [w/b]: ')

    # first_player = input('Who is to make the first move [h/c]: ')
    # first_player = 'h'
    # while first_player not in ['h', 'H', 'c', 'C']:
    #     print('Wrong input. Try again!')
    #     first_player = input('Who is to make the first move [h/c]: ')

    color_mapping = {'w': colors.WHITE, 'b': colors.BLACK}
    first_player_color = color_mapping[first_color.lower()]
    current_player = first_player_color

    start_game(board_size, current_player)


