from . import fcolors


def add_tuples(tuple1, tuple2):
    return tuple(a + b for a, b in zip(tuple1, tuple2))

def lighten_color(color_tuple):
    return tuple(min(chanel + 20, 255) for chanel in color_tuple)

def print_score(white_points, black_points):
    print(f'{fcolors.OKGREEN}############################')
    print(f'### White: {white_points} Black: {black_points} ###')
    print(f'############################{fcolors.ENDC}')

def print_error(text):
    print(f'{fcolors.FAIL}{text}{fcolors.ENDC}')

def print_warning(text):
    print(f'{fcolors.WARNING}{text}{fcolors.ENDC}')

def print_green(text):
    print(f'{fcolors.OKGREEN}{text}{fcolors.ENDC}')