from typing import Dict, List, Tuple

from .utils import add_tuples


def get_clicked_tile_position(
        x: int, 
        y: int, 
        tile_size: int
    ) -> Tuple[int, int]:
    """
    Calculates the row and column indices of a tile based on clicked screen coordinates.
    """
    row = y // tile_size
    column = x // tile_size
    return row, column

def are_neighbours(
        source_tile: Tuple[int, int], 
        destination_tile: Tuple[int, int]
    ) -> bool:
    """
    Checks if two tiles are neighbours on the board.
    """
    if source_tile == destination_tile:
        return False
    x_distance = abs(destination_tile[1] - source_tile[1])
    y_distance = abs(destination_tile[0] - source_tile[0])
    if x_distance > 1 or y_distance > 1:
        return False
    return True

def has_neighbours(
        board_dict: Dict, 
        board_size: int, 
        current_row: int, 
        current_column: int
    ) -> bool:
    """
    Determines if a given tile has any neighbouring tiles with stacks on the board.
    """
    neighbor_positions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    for row_offset, column_offset in neighbor_positions:
        neighbor_row = current_row + row_offset
        neighbor_column = current_column + column_offset
        
        if 0 <= neighbor_row < board_size and 0 <= neighbor_column < board_size:
            if board_dict.get((neighbor_row, neighbor_column)):
                return True

    return False

def is_inside_board(
        tile: Tuple[int, int],
        board_size: int
    ) -> bool:
    """
    Checks if a tile position is within the boundaries of the board.
    """
    return tile[0] >= 0 and tile[1] >= 0 and tile[0] <= board_size-1 and tile[1] <= board_size-1

def find_closest_tiles_with_stacks(
        board_dict: Dict, 
        board_size: int, 
        current_row: int, 
        current_column: int
    ) -> List[Tuple[int, int]]:
    """
    Finds the closest tiles with stacks to a given tile in a diagonal direction.
    """
    left_tile = (current_row-1, current_column-1)
    right_tile = (current_row+1, current_column+1)
    found = False
    closest_tiles = []

    while not found:

        left_tile_h = left_tile
        left_tile_v = left_tile
        right_tile_h = right_tile
        right_tile_v = right_tile

        while left_tile_h != right_tile_v and left_tile_v != right_tile_h:
            if is_inside_board(left_tile_h, board_size) and board_dict[left_tile_h]:
                closest_tiles.append(left_tile_h)
                found = True
            if is_inside_board(left_tile_v, board_size) and  board_dict[left_tile_v] and left_tile_v != left_tile_h:
                closest_tiles.append(left_tile_v)
                found = True
            if is_inside_board(right_tile_h, board_size) and board_dict[right_tile_h]:
                closest_tiles.append(right_tile_h)
                found = True
            if is_inside_board(right_tile_v, board_size) and board_dict[right_tile_v] and right_tile_v != right_tile_h:
                closest_tiles.append(right_tile_v)
                found = True
            left_tile_h = (left_tile_h[0], left_tile_h[1] + 2)
            left_tile_v = (left_tile_v[0] + 2, left_tile_v[1])
            right_tile_h = (right_tile_h[0], right_tile_h[1] - 2)
            right_tile_v = (right_tile_v[0] - 2, right_tile_v[1])

        if is_inside_board(left_tile_h, board_size) and board_dict[left_tile_h]:
            closest_tiles.append(left_tile_h)
            found = True
        if is_inside_board(left_tile_v, board_size) and board_dict[left_tile_v]:
            closest_tiles.append(left_tile_v)
            found = True

        left_tile = (left_tile[0]-1, left_tile[1]-1)
        right_tile = (right_tile[0]+1, right_tile[1]+1)

        if current_row - left_tile[0] >= board_size:
            # To prevent infinite loop
            found = True

    return closest_tiles

def find_closest_directions(
        board_dict: Dict, 
        board_size: int, 
        current_row: int, 
        current_column: int
    ) -> List[Tuple[int, int]]:
    """
    Identifies the directions to the closest tiles with stacks from a given tile.
    """
    closest_tiles = []

    closest_tiles = find_closest_tiles_with_stacks(board_dict, board_size, current_row, current_column)

    if not closest_tiles:
        return closest_tiles
    
    possible_moves = set()

    for tile in closest_tiles:
        direction_row = tile[0] - current_row
        direction_column = tile[1] - current_column

        row_step = 1 if direction_row > 0 else (-1 if direction_row < 0 else 0)
        column_step = 1 if direction_column > 0 else (-1 if direction_column < 0 else 0)

        if abs(direction_row) > abs(direction_column):
            possible_moves.add((row_step, -1))
            possible_moves.add((row_step, 1))
        elif abs(direction_row) < abs(direction_column):
            possible_moves.add((-1, column_step))
            possible_moves.add((1, column_step))
        else:
            possible_moves.add((row_step, column_step))

    return list(possible_moves)

def get_potential_moves(
        board_dict: Dict, 
        board_size: int, 
        selected_row: int, 
        selected_column: int
    ) -> List[Tuple[int, int]]:
    """
    Calculates potential move positions for a selected stack based on the closest stacks in each direction.
    """
    closest_directions = find_closest_directions(board_dict, board_size, selected_row, selected_column)
    potential_moves = [
        add_tuples((selected_row, selected_column), direction)
        for direction in closest_directions
    ]
    return potential_moves

def is_destination_level_higher_than_current_level(
        current_token,
        destination_stack
    ) -> bool:
    """
    Checks if the level of the last token in the destination stack is higher than or equal to the level of the current token.
    """
    return current_token.level <= len(destination_stack)
