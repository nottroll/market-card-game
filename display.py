"""
Alson Lee
Date: 05/04/24

The display module handles simple console output.
"""

MAX_DISPLAY_WIDTH = 60
LPAD = 4

def print_title():
    """
    Prints the game title.
    """
    print('Market making card game')
    print_divider()

def print_divider():
    """
    Prints a divider.
    """
    print('-' * MAX_DISPLAY_WIDTH, '\n')

def print_instructions():
    """
    Prints the game instructions.
    """
    print('If a card is face-down, it is displayed as --')

def show_card_values(suits: list[str], ranks: list[str], 
                     face_card_values: dict[str, int]):
    """
    Prints the corresponding values for each card.
    """
    print('Card values:')
    for rank in ranks:
        print(f'{rank:<2}{"".join(suits)} =', 
              f'{face_card_values[rank] if rank in face_card_values else rank}')

def show_settings(**settings):
    """
    Prints the game settings.
    """
    print('Game settings:')
    for setting, val in settings.items():
        if type(val) is int or type(val) is bool:
            val = str(val)
        if type(val) is list:
            val = ' '.join([str(i) for i in val])
        
        print(setting.replace('_',' ').title(), '=', val.lower().replace('_',' '))
    