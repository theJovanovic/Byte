from typing import List, Dict, Tuple

import utils.colors as colors
from board.token import Token
from utils.movement import get_potential_moves, has_neighbours, is_destination_level_higher_than_current_level, is_inside_board


class AI:

    def __init__(
            self,
            max_points
        ) -> None:
        self.white_points = 0
        self.black_points = 0
        self.max_points = max_points

    def ai_get_next_positions(
            self,
            board_dict,
            board_size,
            player_color: Tuple[int, int, int],
            is_one_stack_left
        ) -> List[Dict[Tuple[int, int], List[Token]]]:
        """
        Generates a list of potential board configurations after one move, 
        given the current state of the board and the player's color.

        This method iterates through all the stacks on the board. For each stack, it determines 
        if a move is possible based on the current player's color and the surrounding tiles. 
        If a move is possible, the method simulates the move, resulting in a new board configuration, 
        which is then added to the list of potential positions.

        Returns:
            A list of dictionaries representing the board configurations after each potential move.
            Each dictionary is similar in structure to board_dict, with the move applied.
        """
        next_positions = []

        for tile, stack in board_dict.items():
            if not stack:
                continue

            tile_has_neighbours = has_neighbours(board_dict, board_size, tile[0], tile[1])
            neighbour_tiles = [
                        (tile[0]-1, tile[1]-1),
                        (tile[0]-1, tile[1]+1),
                        (tile[0]+1, tile[1]+1),
                        (tile[0]+1, tile[1]-1)
                    ]

            for token in stack:
                # Has no neighbours
                if token.level == 1 and token.color == player_color and not tile_has_neighbours:
                    potential_moves = get_potential_moves(board_dict, board_size, tile[0], tile[1])
                    for potential_tile in potential_moves:
                        # Check if potential tile is inside the board
                        if not is_inside_board(potential_tile, board_size):
                            continue

                        potential_tile_stack = board_dict[potential_tile]
                        
                        # Save which token level will need to be reverted
                        revert_level = len(potential_tile_stack) + 1

                        # Save old token level
                        old_token_level = token.level
                        
                        # Change the state
                        board_dict = self.ai_move_stack(board_dict, tile, token.level, potential_tile)

                        # Check if 8-token stack was formed
                        full_stack_formed = len(potential_tile_stack) + len(stack) - (old_token_level - 1) == 8

                        # Check if the last stack formed
                        position_status = False
                        if full_stack_formed:
                            if is_one_stack_left:
                                position_status = True
                            else:
                                white_formed_stack = board_dict[potential_tile][-1].color == colors.WHITE
                                black_formed_stack = board_dict[potential_tile][-1].color == colors.BLACK
                                white_is_about_to_win = self.white_points == (self.max_points // 2)
                                black_is_about_to_win = self.black_points == (self.max_points // 2)
                                if (white_formed_stack and white_is_about_to_win) or (black_formed_stack and black_is_about_to_win):
                                    position_status = True
                            

                        # if is_one_stack_left and full_stack_formed:
                        #     position_status = True
                        # else:
                        #     # Check if the game is over
                        #     white_formed_stack = board_dict[potential_tile][-1].color == colors.WHITE
                        #     black_formed_stack = board_dict[potential_tile][-1].color == colors.BLACK
                        #     white_is_about_to_win = self.white_points == (self.max_points // 2)
                        #     black_is_about_to_win = self.black_points == (self.max_points // 2)
                        #     if full_stack_formed and ((white_formed_stack and white_is_about_to_win) or (black_formed_stack and black_is_about_to_win)):
                        #         position_status = True

                        # Revert the state
                        board_dict = self.ai_move_stack(board_dict, potential_tile, revert_level, tile)

                        next_positions.append((position_status, (tile, token.level, potential_tile, revert_level)))

                # Has neighbours
                if token.color == player_color and tile_has_neighbours:
                    for neighbour_tile in neighbour_tiles:
                        # Check if neighbour tile is inside the board
                        if not is_inside_board(neighbour_tile, board_size):
                            continue

                        neighbour_stack = board_dict[neighbour_tile]

                        # Check if token would have higher level if moved to destination stack
                        if not neighbour_stack or not is_destination_level_higher_than_current_level(token, neighbour_stack):
                            continue

                        # Check if resulting stack would have more than 8 tokens
                        if len(neighbour_stack) + len(stack) - (token.level - 1) > 8:
                            continue

                        # Save which token level will need to be reverted
                        revert_level = len(neighbour_stack) + 1

                        # Save old token level
                        old_token_level = token.level

                        # Change the state
                        board_dict = self.ai_move_stack(board_dict, tile, token.level, neighbour_tile)

                        # Check if 8-token stack was formed
                        full_stack_formed = len(neighbour_stack) + len(stack) - (old_token_level - 1) == 8

                        # Check if the last stack formed
                        position_status = False
                        if full_stack_formed:
                            if is_one_stack_left:
                                position_status = True
                            else:
                                white_formed_stack = board_dict[neighbour_tile][-1].color == colors.WHITE
                                black_formed_stack = board_dict[neighbour_tile][-1].color == colors.BLACK
                                white_is_about_to_win = self.white_points == (self.max_points // 2)
                                black_is_about_to_win = self.black_points == (self.max_points // 2)
                                if (white_formed_stack and white_is_about_to_win) or (black_formed_stack and black_is_about_to_win):
                                    position_status = True

                        # position_status = False
                        # if is_one_stack_left and full_stack_formed:
                        #     position_status = True
                        # else:
                        #     # Check if the game is over
                        #     white_formed_stack = board_dict[neighbour_tile][-1] == colors.WHITE
                        #     black_formed_stack = board_dict[neighbour_tile][-1] == colors.BLACK
                        #     white_is_about_to_win = self.white_points == self.max_points // 2
                        #     black_is_about_to_win = self.black_points == self.max_points // 2
                        #     if full_stack_formed and ((white_formed_stack and white_is_about_to_win) or (black_formed_stack and black_is_about_to_win)):
                        #         position_status = True

                        # Revert the state
                        board_dict = self.ai_move_stack(board_dict, neighbour_tile, revert_level, tile)
                        
                        next_positions.append((position_status, (tile, token.level, neighbour_tile, revert_level)))

        return next_positions

    def ai_move_stack(
            self, 
            board_dict, 
            source_tile: Tuple[int, int], 
            source_token_level: int, 
            destination_tile: Tuple[int, int]
        ) -> Dict[Tuple[int, int], List[Token]]:
        """
        Simulates the movement of a stack of tokens from a source tile to a destination tile on the board.

        This function creates a deep copy of the current board state and then moves a specified 
        number of tokens from the source tile to the destination tile. The movement respects the 
        rules of the game, such as token stacking order and maximum stack height.

        Returns:
            A new dictionary representing the state of the board after the move. This dictionary 
            has the same structure as board_dict but reflects the changes after the move.
        """
        # new_board = copy.deepcopy(board_dict)
        new_board = board_dict
        source_token_index = source_token_level - 1
        destination_max_level = len(new_board[destination_tile])

        selected_tokens = new_board[source_tile][source_token_index:]
        for token in selected_tokens:
            token.move(destination_tile[0], destination_tile[1], destination_max_level+1)
            destination_max_level += 1

        new_board[destination_tile] = [*new_board[destination_tile], *selected_tokens]
        new_board[source_tile] = new_board[source_tile][:source_token_index]

        return new_board
    
    def ai_make_move(
            self, 
            board_dict,
            board_size,
            current_player_color,
            is_one_stack_left
        ) -> None:

        is_maximizing_player = current_player_color == colors.WHITE
        print('AI is thinking...', end=' ', flush=True)
        best_heuristic_value, best_move = self.minimax(board_dict, board_size, 3, is_maximizing_player, is_one_stack_left)
        print(f'H = {best_heuristic_value}')

        return best_move

    def minimax(
            self, 
            board_dict: Dict[Tuple[int, int], List[Token]],
            board_size: int,
            depth: int,
            is_maximizing_player: bool,
            is_one_stack_left: bool,
            alpha=float('-inf'), 
            beta=float('inf'),
            prev_player_next_positions = 1
        ) -> Tuple[int, Dict[Tuple[int, int], List[Token]]]:
        if depth == 0:
            return self.heuristic(board_dict, board_size), board_dict

        player_color = colors.WHITE if is_maximizing_player else colors.BLACK
        best_move = None
        next_positions = self.ai_get_next_positions(board_dict, board_size, player_color, is_one_stack_left)

        if len(next_positions) == 0:
            if prev_player_next_positions == 0 and len(next_positions) == 0:
                # For preventing infinte loop
                heuristic_value = self.heuristic(board_dict, board_size)
            else:
                # Default algorithm path
                heuristic_value, _ = self.minimax(board_dict, board_size, depth, not is_maximizing_player, is_one_stack_left, alpha, beta, len(next_positions))
            if is_maximizing_player:
                if heuristic_value > float('-inf'):
                    best_value = heuristic_value
            else:
                if heuristic_value < float('inf'):
                    best_value = heuristic_value
            return best_value, best_move
        

        if is_maximizing_player:
            best_value = float('-inf')
            for next_position in next_positions:
                next_position_is_final = next_position[0]
                next_board_instructions = next_position[1]

                source_tile = next_board_instructions[0]
                token_level = next_board_instructions[1]
                destination_tile = next_board_instructions[2]
                token_revert_level = next_board_instructions[3]

                next_board = self.ai_move_stack(board_dict, source_tile, token_level, destination_tile)

                if next_position_is_final:
                    heuristic_value = self.heuristic(next_board, board_size)
                else:
                    heuristic_value, _ = self.minimax(next_board, board_size, depth - 1, False, is_one_stack_left, alpha, beta)

                if heuristic_value > best_value:
                    best_value = heuristic_value
                    best_move = next_board_instructions

                next_board = self.ai_move_stack(board_dict, destination_tile, token_revert_level, source_tile)

                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break

            return best_value, best_move
        
        else:
            best_value = float('inf')
            for next_position in next_positions:
                next_position_is_final = next_position[0]
                next_board_instructions = next_position[1]

                source_tile = next_board_instructions[0]
                token_level = next_board_instructions[1]
                destination_tile = next_board_instructions[2]
                token_revert_level = next_board_instructions[3]

                next_board = self.ai_move_stack(board_dict, source_tile, token_level, destination_tile)

                if next_position_is_final:
                    heuristic_value = self.heuristic(next_board, board_size)
                else:
                    heuristic_value, _ = self.minimax(next_board, board_size, depth - 1, True, is_one_stack_left, alpha, beta)

                if heuristic_value < best_value:
                    best_value = heuristic_value
                    best_move = next_board_instructions

                next_board = self.ai_move_stack(board_dict, destination_tile, token_revert_level, source_tile)

                beta = min(beta, best_value)
                if beta <= alpha:
                    break

            return best_value, best_move

    def heuristic(
            self, 
            board_dict: Dict[Tuple[int, int], List[Token]],
            board_size: int
        ) -> int:
        score = 0
        white_tokens = 0
        black_tokens = 0

        for tile, stack in board_dict.items():
            if not stack:
                continue

            # Count the tokens on the stack
            for token in stack:
                if token.color == colors.WHITE:
                    white_tokens += 1
                else:
                    black_tokens += 1

            # Stack Height Value
            stack_height = len(stack)
            stack_height_score = 2 * (stack_height - 1)
            stack_height_score = stack_height_score if stack[-1].color == colors.WHITE else -stack_height_score

            # Mobility Score
            mobility = len(get_potential_moves(board_dict, board_size, tile[0], tile[1]))
            mobility_score = mobility * 2
            mobility_score = mobility_score if stack[-1].color == colors.WHITE else -mobility_score

            # Control of Center
            center_control_score = 0
            if self.is_center(tile, board_size):
                center_control_score = 2 if stack[-1].color == colors.WHITE else -2

            # Check for 8-token stack and add 100 points to the owner
            eight_token_stack_score = 0
            if stack_height == 8:
                eight_token_stack_score = 100 if stack[-1].color == colors.WHITE else -100                

            score += stack_height_score + mobility_score + center_control_score + eight_token_stack_score

        score += white_tokens - black_tokens
        
        return score

    def is_center(self, tile, board_size):
        center_area = range(board_size // 4, 3 * board_size // 4)
        return tile[0] in center_area and tile[1] in center_area