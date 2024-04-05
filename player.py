"""
Alson Lee
Date: 17/03/24

Market making card game
"""

"""
Class to represent a player in the market making card game.
"""
class Player:
    def __init__(self, balance = 500) -> None:
        self.balance = balance
        