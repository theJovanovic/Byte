from typing import Tuple, Union


class Token:
    id = 0

    def __init__( 
            self, 
            row: int, 
            column: int, 
            color: Tuple[int, int, int], 
            width: int, 
            height: int, 
            level: int = 1
        ) -> None:
        self.row = row
        self.column = column
        self.level = level
        self.color = color
        self.width = width
        self.height = height
        self.selected = False
        self.border_thickness = 1
        self.id = Token.id

        Token.id += 1

    def change_selected_status(
            self, 
            status: Union[bool, None]=None
        ) -> None:
        """
        Changes the selected status of the token.

        This function toggles the selected status of the token. If no specific status is provided,
        it simply inverts the current status. If a specific status (True or False) is provided,
        the token's selected status is set to that value.
        """
        if status is None:
            self.selected = not self.selected
        else:
            self.selected = status

    def move(
            self,
            dest_row: int, 
            dest_column: int, 
            dest_level: int
        ) -> None:
        """
        Moves the token to a new position on the board.

        This function updates the token's position by setting its row, column, and level to the 
        specified destination values. This is typically used to reflect the token's new position 
        after a move in the game.
        """
        self.row = dest_row
        self.column = dest_column
        self.level = dest_level

    def __repr__(
            self
        ) -> str:
        return f'id:{self.id};row:{self.row};column:{self.column};level:{self.level};'
