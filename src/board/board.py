from typing import List, Dict, Tuple

from .token import Token
from utils import colors
from utils.movement import get_clicked_tile_position, are_neighbours, get_potential_moves, has_neighbours, is_destination_level_higher_than_current_level, is_inside_board
from utils.utils import lighten_color, print_error, print_green, print_score, print_warning
from ai.ai import AI


class Board:

    def __init__(
            self,
            board_size: int,
            tile_size: int,
            current_player: Tuple[int, int, int]
        ) -> None:
        self.board: Dict = {}
        self.white_points: int = 0
        self.black_points: int = 0
        self.tile_size: int = tile_size
        self.board_size: int = board_size
        self.max_points = (self.board_size ** 2 - 2 * self.board_size) // 16
        self.selected_tokens: List[Token] = []
        self.board_dark: Tuple[int, int, int] = colors.BROWN
        self.board_light: Tuple[int, int, int] = colors.BEIGE
        self.current_player = current_player
        self.ai = AI(self.max_points)

    def change_selected_tokens_status(
            self
        ) -> None:
        """
        Toggles the selected status of all tokens currently in the selected tokens list.

        This function iterates over the tokens in `self.selected_tokens` and calls the `change_selected_status` 
        method on each token. It is used to either select or deselect a group of tokens, based on their current 
        status. The function effectively reverses the selected state of each token in the list.
        """
        [selected_token.change_selected_status() for selected_token in self.selected_tokens]

    def initialize_board(
            self
        ) -> None:
        """
        Initializes the game board with tokens at the start of the game.

        This function sets up the initial state of the board for a new game. It places tokens on each tile of the board, 
        except for the first and last rows. The tokens are alternately colored black and white, with their width 
        and height set relative to the tile size. The tokens are positioned only on tiles where the sum of the row and 
        column indices is even, creating a checkerboard pattern.

        The board is represented as a dictionary where keys are (row, column) tuples for the tiles, and the values are lists 
        of Token objects representing the stacks of tokens on each tile.
        """
        token_width = int(self.tile_size * 0.8)
        token_height = self.tile_size // 8
        self.board = {
            (row, column): [] if row in (0, self.board_size - 1) else [
                Token(row, column, colors.BLACK if row % 2 else colors.WHITE, token_width, token_height, 1)
            ]
            for row in range(self.board_size)
            for column in range(self.board_size)
            if (row % 2 == column % 2)
        }

        # self.board = {
        #         (0,0): [],
        #         (0,2): [],
        #         (0,4): [],
        #         (0,6): [],
        #         (1,1): [],
        #         (1,3): [],
        #         (1,5): [],
        #         (1,7): [],

        #         (2,0): [],
        #         (2,2): [],
        #         (2,4): [
        #             Token(2,4,colors.WHITE, 80, 15, 1),
        #             Token(2,4,colors.BLACK, 80, 15, 2),
        #             Token(2,4,colors.BLACK, 80, 15, 3),
        #             Token(2,4,colors.WHITE, 80, 15, 4),
        #             Token(2,4,colors.BLACK, 80, 15, 5),
        #             Token(2,4,colors.WHITE, 80, 15, 6),
        #         ],
        #         (2,6): [
        #             Token(2,6,colors.WHITE, 80, 15, 1),
        #             Token(2,6,colors.BLACK, 80, 15, 2),
        #             Token(2,6,colors.WHITE, 80, 15, 3),
        #             Token(2,6,colors.BLACK, 80, 15, 4),
        #             Token(2,6,colors.BLACK, 80, 15, 5),
        #         ],

        #         (3,1): [],
        #         (3,3): [
        #             Token(3,3,colors.WHITE, 80, 15, 1),
        #             Token(3,3,colors.WHITE, 80, 15, 2),
        #             Token(3,3,colors.BLACK, 80, 15, 3),
        #             Token(3,3,colors.WHITE, 80, 15, 4),
        #             Token(3,3,colors.BLACK, 80, 15, 5),
        #             Token(3,3,colors.WHITE, 80, 15, 6),
        #             Token(3,3,colors.BLACK, 80, 15, 7),
        #         ],
        #         (3,5): [],
        #         (3,7): [],

        #         (4,0): [],
        #         (4,2): [],
        #         (4,4): [
        #             Token(4,4,colors.BLACK, 80, 15, 1),
        #             Token(4,4,colors.WHITE, 80, 15, 2),
        #             Token(4,4,colors.BLACK, 80, 15, 3),
        #             Token(4,4,colors.WHITE, 80, 15, 4),
        #             Token(4,4,colors.BLACK, 80, 15, 5),
        #             Token(4,4,colors.WHITE, 80, 15, 6),
        #         ],
        #         (4,6): [],

        #         (5,1): [],
        #         (5,3): [],
        #         (5,5): [],
        #         (5,7): [],

        #         (6,0): [],
        #         (6,2): [],
        #         (6,4): [],
        #         (6,6): [],
        #         (7,1): [],
        #         (7,3): [],
        #         (7,5): [],
        #         (7,7): []
        #     }


    def change_clicked_stack_status(
            self,
            x: int,
            y: int
        ) -> None:
        """
        Changes the selected status of tokens in a stack based on the clicked position.

        This function determines which stack on the board corresponds to the clicked position (x, y) and:
        - If the clicked token belongs to the opposite player, it aborts the selection.
        - If the clicked token is already selected, it deselects it.
        - If the clicked token is not already selected, it deselects any previously selected tokens and 
        selects the new tokens from the clicked stack starting from the clicked token to the top of the stack.
        """
        row, column = get_clicked_tile_position(x, y, self.tile_size)

        if (row, column) not in self.board:
            return
        
        stack = self.board[(row, column)]
        for i in range(len(stack)):
            token = stack[i]
            tile_padding = (self.tile_size - token.width) / 2
            token_x = token.column * self.tile_size + tile_padding
            token_y = (token.row + 1) * self.tile_size - token.height * token.level

            token_x_min = token_x
            token_x_max = token_x + token.width
            token_y_min = token_y
            token_y_max = token_y + token.height

            if token_x_min <= x <= token_x_max and token_y_min <= y <= token_y_max:
                # Abort if opposite player token has been attempted to select
                if not self.is_token_by_current_player(token):
                    return

                # If the clicked token is already selected, deselect it
                if self.selected_tokens and token == self.selected_tokens[0]:
                    self.change_selected_tokens_status()
                    self.selected_tokens = []
                    return
                
                # Deselect old tokens
                self.change_selected_tokens_status()
                self.selected_tokens = []

                # Select new tokens
                self.selected_tokens = [stack[j] for j in range(i, len(stack))]
                self.change_selected_tokens_status()

    def move_stack(
            self,
            row: int,
            column: int
        ) -> bool:
        """
        Attempts to move the selected stack of tokens to a new tile on the board.

        This function performs several checks and actions to move a stack:
        - Verifies that tokens are selected for movement.
        - Ensures the destination tile is valid and not the same as the source tile.
        - Checks if the destination tile is within a valid range (neighbouring tiles).
        - Validates the move based on the game rules, such as stack height and potential moves.
        - Updates the board state and token positions if the move is valid.
        - Checks for the creation of a full stack (size 8) and handles scoring and winner determination.
        - Manages player turns after the move.

        Parameters:
            row (int): The row index of the destination tile.
            column (int): The column index of the destination tile.

        Returns:
            bool: True if the move results in a winning condition, False otherwise.
        """
        is_winning_move = False

        # Check if any token was selected
        selected_tokens_count = len(self.selected_tokens)
        if selected_tokens_count == 0:
            print_warning("No token was selected")
            return is_winning_move

        # Check if row, column are playable tiles
        if (row, column) not in self.board:
            print_error("Tile is not playable")
            return is_winning_move
        
        # Check if destination tile is the same as current tile
        if self.is_selected_tile(row, column):
            print_warning("Source and destination tiles are same")
            return is_winning_move
        
        current_row = self.selected_tokens[0].row
        current_column = self.selected_tokens[0].column

        # Check if tiles are in neighbourhood
        if not are_neighbours((current_row, current_column), (row, column)):
            print_error("Destination tile is too far away")
            return is_winning_move

        current_tile_tokens_count = len(self.board.get((current_row, current_column), []))
        destination_stack = self.board.get((row, column), [])
        destination_tokens_count = len(destination_stack)

        # Check if current tile has neighbours
        if has_neighbours(self.board, self.board_size, current_row, current_column):
            # Check if token would have higher level if moved to destination stack
            if not is_destination_level_higher_than_current_level(self.selected_tokens[0], destination_stack):
                print_error("You are attempting to move token to lower or equal level")
                return is_winning_move
        else:
            # Check if whole stack is selected
            if self.selected_tokens[0].level != 1:
                print_warning("Whole stack must be selected")
                return is_winning_move
            # Check if destination tile is in the list of potential moves
            if (row, column) not in get_potential_moves(self.board, self.board_size, current_row, current_column):
                print_error("Tile is not playable")
                return is_winning_move

        # Check if resulting stack would have more than 8 tokens
        resulting_stack_size = selected_tokens_count + destination_tokens_count
        if resulting_stack_size > 8:
            print_error(f"You are attempting to make stack of size {resulting_stack_size}")
            return is_winning_move

        # Update old tile in board dictionary
        self.board[(current_row, current_column)] = self.board[(current_row, current_column)][:current_tile_tokens_count - selected_tokens_count]

        # Update token objects
        for token in self.selected_tokens:
            token.move(row, column, destination_tokens_count + 1)
            destination_tokens_count += 1

        # Update new tile in board dictionary
        self.board[(row, column)] = [*self.board[(row, column)], *self.selected_tokens]

        # Deselect tokens
        self.change_selected_tokens_status()
        self.selected_tokens = []

        # Check if stack of size 8 has been created
        if len(self.board[(row, column)]) == 8:
            self.handle_full_stack_creation(row, column)

        # Check if there is a winner
        is_winning_move = self.check_for_winner()

        # Change current player
        if not is_winning_move:
            self.change_current_player()

        return is_winning_move

    def current_player_has_valid_move(
            self
        ) -> bool:
        """
        Determines if the current player has any valid moves available.

        This function iterates over all the tiles on the board. For each tile with a stack, it checks:
        - If the stack has no neighbours and the bottom token of the stack belongs to the current player, 
        indicating a valid move.
        - If the stack has neighbours, it evaluates whether there's a valid move to a higher level in any 
        neighbouring stack.
        """
        has_valid_moves = False

        for tile, stack in self.board.items():
            if not stack:
                continue

            current_row = tile[0]
            current_column = tile[1]

            # If stack has no neighbours
            if not has_neighbours(self.board, self.board_size, current_row, current_column):
                # If current players token is on the bottom, the player has a valid move
                if self.is_token_by_current_player(stack[0]):
                    has_valid_moves = True
                    break

            neighbour_tiles = [
                (current_row - 1, current_column - 1),
                (current_row - 1, current_column + 1),
                (current_row + 1, current_column + 1),
                (current_row + 1, current_column - 1),
            ]
            has_valid_moves_from_current_position = False

            for neighbour_tile in neighbour_tiles:
                # Check if possible destination tile is inside the board
                if not is_inside_board(neighbour_tile, self.board_size):
                    continue
                # Check if possible destination tile has a stack
                destination_stack = self.board[neighbour_tile]
                if not destination_stack:
                    continue
                # Check if current stack has a token that can be moved to higher level in destination stack
                if not self.has_valid_move_from_current_stack_to_destination_stack(stack, destination_stack):
                    continue
                has_valid_moves_from_current_position = True
                break

            if has_valid_moves_from_current_position:
                has_valid_moves = True
                break

        return has_valid_moves

    def has_valid_move_from_current_stack_to_destination_stack(
            self,
            current_stack,
            destination_stack
        ) -> bool:
        """
        Checks if current stack has a token that can be moved to a higher level in destination stack
        """
        has_valid_move_from_current_position = False
        for token in current_stack:
            # Check if token belongs to current player
            if not self.is_token_by_current_player(token):
                continue
            # Check if token would have higher level if moved to destination stack
            if not is_destination_level_higher_than_current_level(token, destination_stack):
                continue
            # Check if resulting stack would have more than 8 tokens
            if len(current_stack) + len(destination_stack) - (token.level - 1) > 8:
                continue
            has_valid_move_from_current_position = True
            break

        return has_valid_move_from_current_position

    def determine_tile_color(
            self,
            row: int,
            column: int
        ) -> Tuple[int, int, int]:
        """
        Determines the color of a specific tile on the board.
        
        This function calculates the tile color based on its position and the current game state. It first 
        retrieves the base color of the tile. If the tile should be highlighted (as determined by 
        `should_highlight_tile`) and the addition of the selected stack to this tile would not exceed the maximum 
        stack size, it lightens the base color. Otherwise, it returns the base color.
        """
        base_color = self.get_base_tile_color(row, column)
        destination_tile_tokens_count = len(self.board.get((row, column), []))
        selected_stack_tokens_count = len(self.selected_tokens)
        exceeds_max_stack_size = (destination_tile_tokens_count + selected_stack_tokens_count) > 8
        if self.should_highlight_tile(row, column) and not exceeds_max_stack_size:
            return lighten_color(base_color)
        return base_color

    def get_base_tile_color(
            self,
            row: int,
            column: int
        ) -> Tuple[int, int, int]:
        """
        Retrieves the base color of a tile on the board based on its position.

        This function determines the color of a tile using a checkerboard pattern. It returns the dark color
        for tiles where the sum of the row and column indices is even, and the light color for tiles where
        this sum is odd.
        """
        if (row + column) % 2 == 0:
            return self.board_dark
        else:
            return self.board_light

    def should_highlight_tile(
            self,
            row: int,
            column: int
        ) -> bool:
        """
        Determines whether a specific tile should be highlighted based on the current game state.

        This function checks if the tile at the specified (row, column) position should be highlighted. 
        Highlighting occurs under the following conditions:
        - If there are no selected tokens, no tile is highlighted.
        - If the tile is a valid destination for the selected stack. This includes:
        - Being a neighboring tile to the selected stack and having a valid move from the current stack to the destination stack.
        - Being within the potential moves for the selected stack, if the selected stack has no neighbors.
        """
        if not self.selected_tokens:
            return False

        selected_tile_row, selected_tile_column = self.get_selected_tile_position()
        is_neighbour_to_selected_tile = are_neighbours((selected_tile_row, selected_tile_column), (row, column))

        destination_stack = self.board.get((row, column), [])
        has_valid_move = self.has_valid_move_from_current_stack_to_destination_stack(self.selected_tokens, destination_stack)

        if has_neighbours(self.board, self.board_size, selected_tile_row, selected_tile_column):
            return not self.is_selected_tile(row, column) and is_neighbour_to_selected_tile and has_valid_move
        else:
            # If selected token is not on the bottom, stack can not be moved - no tile highlighted
            if self.selected_tokens[0].level != 1:
                return False
            potential_moves = get_potential_moves(self.board, self.board_size, selected_tile_row, selected_tile_column)
            return (row, column) in potential_moves

    def get_selected_tile_position(
            self
        ) -> Tuple[int, int]:
        """
        Retrieves the position of the tile corresponding to the first token in the selected tokens list.

        This function returns the row and column indices of the tile where the first token in the 
        `selected_tokens` list is located. It assumes that there is at least one token in the 
        `selected_tokens` list.
        """
        return self.selected_tokens[0].row, self.selected_tokens[0].column

    def is_selected_tile(
            self,
            row: int,
            column: int
        ) -> bool:
        """
        Checks if the tile at the specified position is the one with the currently selected token.

        This function determines whether the tile located at the given row and column coordinates
        corresponds to the tile of the first token in the `selected_tokens` list. If there are no tokens 
        in `selected_tokens`, it returns False.
        """
        if not self.selected_tokens:
            return False
        selected_row = self.selected_tokens[0].row
        selected_column = self.selected_tokens[0].column
        return (selected_row, selected_column) == (row, column)

    def is_token_by_current_player(
            self,
            token: Token
        ) -> bool:
        """
        Determines if the given token belongs to the current player.

        This function checks if the color of the specified token matches the color associated with the
        current player. It's used to verify whether an action or move can be attributed to the current 
        player based on the token they are interacting with.
        """
        return token.color == self.current_player

    def get_current_player_color(
            self
        ) -> Tuple[int, int, int]:
        """
        Retrieves the color associated with the current player.

        This function returns the RGB color tuple that represents the current player. This color 
        is used to identify which player's turn it is in the game and can be used for various
        game elements like token colors or UI indicators.
        """
        return self.current_player
    
    def change_current_player(
            self
        ) -> None:
        """
        Switches the current player from white to black, or from black to white, if the next player has valid moves.

        This function first checks if the next player has any valid moves. If valid moves are available, it alternates 
        the `current_player` attribute between the two player colors. If the current player is white, it changes to black, 
        and vice versa. If the next player does not have any valid moves, it prints a message indicating that the player's 
        move is skipped. This function is used to update the game state to reflect which player's turn it is after a move 
        has been made, considering the availability of valid moves for the next player.
        """
        self.current_player = colors.BLACK if self.current_player == colors.WHITE else colors.WHITE
        if not self.current_player_has_valid_move():
            self.current_player = colors.BLACK if self.current_player == colors.WHITE else colors.WHITE
            skipped_player_color_name = 'White' if self.current_player == colors.BLACK else 'Black'
            print(f"{skipped_player_color_name} move skipped because there are no valid moves")
    
    def make_ai_move(
            self
        ) -> None:
        """
        Executes a move for the AI player and then switches the current player.

        This function allows the AI to make a move in the game. It first retrieves the color of the 
        current player and then calls the AI's `ai_make_move` method with the current game state and 
        the player color. After the AI move is made, it switches the current player to allow the 
        next player to make their move.
        """
        # Deselect any selected tokens
        self.change_selected_tokens_status()
        self.selected_tokens = []

        # Make a move
        is_one_stack_left = True if self.get_num_of_remaining_stacks() == 1 else False
        self.ai.white_points = self.white_points
        self.ai.black_points = self.black_points
        new_board = self.ai.ai_make_move(self.board, self.board_size, self.current_player, is_one_stack_left)

        # If new_board is None, then AI should skip a move
        if new_board:
            source_tile = new_board[0]
            token_level = new_board[1]
            destination_tile = new_board[2]
            self.ai.ai_move_stack(self.board, source_tile, token_level, destination_tile)

        # Check if stack of size 8 has been created
        full_stack_tile = self.get_full_stack_tile()
        if full_stack_tile:
            self.handle_full_stack_creation(full_stack_tile[0], full_stack_tile[1])

        # Check if there is a winner
        is_winning_move = self.check_for_winner()

        # Change current player
        if not is_winning_move:
            self.change_current_player()

        return is_winning_move
    
    def get_num_of_remaining_stacks(self):
        return self.max_points - (self.white_points + self.black_points)
    
    def get_full_stack_tile(self) -> Tuple[int, int]:
        for tile, stack in self.board.items():
            if not stack:
                continue
            if len(stack) == 8:
                return tile
        return None
    
    def handle_full_stack_creation(self, row, column):
        """
        Handles the scenario when a full stack of size 8 is created on the board.

        When a stack reaches the maximum size of 8, this function is called to perform several actions:
        1. Prints a message indicating that a full stack was created.
        2. Updates the points for the player who completed the stack, based on the color of the top token.
        3. Removes all tokens from the completed stack.
        4. Checks for a winner after the stack is completed.

        Returns:
            bool: True if the completion of the stack results in a winner, False otherwise.
        """
        print_green("Stack with size 8 was created")
        # Update the points
        if self.board[(row, column)][-1].color == colors.WHITE:
            self.white_points += 1
        else:
            self.black_points += 1
        # Print the score
        print_score(self.white_points, self.black_points)
        # Delete the tokens
        self.board[(row, column)] = []
        # Return True if there is a winner, otherwise False
        return self.check_for_winner()
    
    def check_for_winner(
            self
        ) -> bool:
        """
        Checks if either player has reached the winning point total.

        This function calculates the total number of points required to win the game based on the 
        size of the board. It then checks if either the white or black player has reached or 
        surpassed this winning point total. If a player has won, it sets `is_winning_move` to True.

        If no player has won yet, the function prints the current score for both players.
        """
        is_winning_move = False
        winning_point = self.max_points // 2 + 1
        if self.white_points == winning_point or self.black_points == winning_point:
            is_winning_move = True
        return is_winning_move