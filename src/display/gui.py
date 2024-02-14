import pygame
from typing import List, Tuple

from utils import colors
from board.board import Board
from board.token import Token


class GUI:

    def __init__(
            self, 
            screen: pygame.Surface
        ) -> None:
        self.screen = screen

    def draw_board(
            self, 
            board: Board
        ) -> None:
        """
        Draws the game board and the tokens on it.

        This function iterates over each tile of the provided game board, drawing the tiles and any 
        token stacks on them. For each tile, it first determines the tile color and then draws the 
        tile using Pygame's rectangle drawing functionality. If a stack of tokens is present on a tile, 
        it calls the `draw_stack` method to render the tokens in that stack.
        """
        for row in range(board.board_size):
            for column in range(board.board_size):

                color = board.determine_tile_color(row, column)
                tile_rect = (column*board.tile_size, row*board.tile_size, board.tile_size, board.tile_size)
                pygame.draw.rect(self.screen, color, tile_rect)

                if (row, column) in board.board:
                    stack = board.board[(row, column)]
                    self.draw_stack(stack, board.tile_size)

    def draw_stack(
            self, 
            stack: List[Token], 
            tile_size: int
        ) -> None:
        """
        Draws a stack of tokens on a tile.

        This function iterates through each token in the provided stack and calls the `draw_token` 
        method to render each token on the screen. The tokens are drawn based on their position in 
        the stack and the size of the tile they are on.
        """
        for token in stack:
            self.draw_token(token, tile_size)

    def draw_token(
            self, 
            token: Token, 
            tile_size: int
        ) -> None:
        """
        Draws an individual token on the board.

        This function calculates the position and size of the token based on its attributes and the tile size.
        It then draws the token on the board using Pygame, including a border around the token which 
        varies in thickness based on whether the token is currently selected.
        """
        tile_padding = (tile_size - token.width) / 2
        token_color = token.color
        token_size = (token.width, token.height)
        token_thickness = 3 if token.selected else token.border_thickness
        token_position_x = token.column*tile_size + tile_padding
        token_position_y = (token.row+1)*tile_size - token.height*(token.level)
        token_position = (token_position_x, token_position_y)

        border_rect = [
            token_position[0] - token_thickness,
            token_position[1] - token_thickness,
            token_size[0] + token_thickness * 2,
            token_size[1] + token_thickness * 2
        ]
        border_color = self.get_border_color(token)

        pygame.draw.rect(self.screen, border_color, border_rect)    
        pygame.draw.rect(self.screen, token_color, (token_position, token_size))

    def get_border_color(
            self, 
            token: Token
        ) -> Tuple[int, int, int]:
        """
        Determines the border color for a given token.

        This function returns a specific color for the token's border. If the token is selected, it 
        returns green. If the token is white, it returns black; otherwise, it returns white. This 
        helps visually differentiate tokens based on their state and color.
        """
        if token.selected:
            return colors.GREEN
        elif token.color == colors.WHITE:
            return colors.BLACK
        else:
            return colors.WHITE

    def update_caption(
            self, 
            current_player_color: Tuple[int, int, int]
        ) -> None:
        """
        Updates the window caption to indicate the current player's turn.

        This function sets the caption of the Pygame window to reflect whose turn it is based on the 
        color of the current player. The caption will display 'Byte - WHITE TURN' or 'Byte - BLACK TURN' 
        accordingly.
        """
        if current_player_color == colors.WHITE:
            pygame.display.set_caption('Byte - WHITE TURN')
        else:
            pygame.display.set_caption('Byte - BLACK TURN')