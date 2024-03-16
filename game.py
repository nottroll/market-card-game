"""
Alson Lee
Date: 15/03/24

Market making card game
"""

import copy
import random as rand
import time
import threading
from itertools import product, permutations

from deck import Card, Deck
from player import Player

"""
Game settings
"""
CARDS_PER_ROUND = 3
ROUNDS = 3
TIME_LIMIT = 60

MARKET_EVENTS = False

START_BALANCE = 500
SHOW_BALANCE = True

SUITS_1 = ['♥', '♦', '♣', '♠']
SUITS_2 = ['🐄', '🐍', '🐕', '🐬', '🐞']
SUITS_3 = ['⚽', '⭐', '❌', '🔶', '✅', '♒', '🔵']

RANKS = [str(i) for i in range(2, 11)] + ['J', 'Q', 'K', 'A']
FACE_CARD_VALUES_1 = {'J': 11, 'Q': 12, 'K': 13, 'A': 14}
FACE_CARD_VALUES_2 = {'A': 1, 'J': 11, 'Q': 12, 'K': 13}

class Round:
    def __init__(self, round_num=1, picked_cards = [], 
                 is_face_up = [], card_values={}) -> None:
        self.round_num: int = round_num
        self.picked_cards: list[Card] = picked_cards
        self.is_face_up: list[bool] = is_face_up
        self.card_values: dict[int] = card_values
        self.order = None
        self.order_unit = 0
        self.spread = ()

        self.player_balance = 0
        self.player_true_pl = 0
        self.player_input_pl = 0

    def __str__(self) -> str:
        return (  f'Round:  {self.round_num}' + '\n'
                + f'Cards:  {self.show_round()} (EV = {self.calculate_ev()})' + '\n' 
                + f'Reveal: {" ".join([str(card) for card in self.picked_cards])} (Actual = {self.sum_value()})' + '\n'
                + f'Spread: {self.spread[0]} at {self.spread[1]}' + '\n'
                + f'Order:  {self.order} {self.order_unit if self.order_unit > 0 else ""}')

    def show_round(self) -> str:
        show = []
        for card, is_face_up in zip(self.picked_cards, self.is_face_up):
            if is_face_up:
                show.append(str(card))
            else:
                show.append('--')
        return ' '.join(show)

    def rand_face_up(self) -> None:
        face_up = []
        face_up_limit = len(self.picked_cards) // 3
        face_up_chance = 0.5

        for idx in range(len(self.picked_cards)):
            if idx < face_up_limit:
                roll = rand.randint(1, 100) / 100
                if roll <= face_up_chance:
                    face_up.append(True)
                else:
                    face_up.append(False)
            else:
                face_up.append(False)
        self.is_face_up = face_up

    def calculate_ev(self) -> float:
        ev = 0
        for card, is_face_up in zip(self.picked_cards, self.is_face_up):
            if is_face_up:
                ev += self.card_values[card.rank]
            else:
                ev += 8  # TODO: FIX THIS 
        return ev

    def sum_value(self) -> int:
        total = 0
        for card in self.picked_cards:
            total += self.card_values[card.rank]
        return total

    def calculate_spread(self) -> tuple:
        ev = self.calculate_ev()

        offset_limit = int(ev / 5)
        offset = rand.randint(-offset_limit, offset_limit)

        spread_width = rand.randint(2, 6)
        self.spread = ev + offset - spread_width // 2, ev + offset + spread_width // 2
        return self.spread
    
    def calculate_pl(self) -> int:
        if self.order == 'Buy':
            pl = (self.sum_value() - self.spread[1]) * self.order_unit
        elif self.order == 'Sell':    
            pl = (self.spread[0] - self.sum_value()) * self.order_unit
        else:
            pl = 0
        self.player_true_pl = pl
        return self.player_true_pl

    def calculate_distribution(self) -> None:
        # p = product(RANKS, SUITS_1)
        # p = [f'{r}{s}' for r, s in list(p)]

        # print(p)
        # c = permutations(p, CARDS_PER_ROUND)
        # print(list(c))
        pass


    def place_order(self, order: str, units: int) -> None:
        self.order = order
        self.order_unit = units

    def add_card(self, card: Card) -> None:
        self.picked_cards.append(card)
        self.is_face_up.append(False)

    def clear_cards(self) -> None:
        self.picked_cards.clear()
        self.is_face_up.clear()


class Timer:
    def __init__(self, turn_time = 0) -> None:
        self.turn_time = turn_time


def main() -> None:
    print('Market making card game')

    ranks = RANKS 
    suits = SUITS_1
    values = {}
    for rank in ranks:
        if rank.isnumeric():
            values[rank] = int(rank)
        else:
            values[rank] = FACE_CARD_VALUES_1[rank]

    game_deck = Deck(ranks, suits)
    game_deck.shuffle()
    # print('Deck:', str(game_deck), '\n')

    player = Player(START_BALANCE)

    game_rounds: list[Round] = []
    for r in range(1, ROUNDS + 1):
        print('-' * 30, '\n', f'Round {r}', '\n')

        # Create round and pick cards
        round = Round(round_num=r, card_values=values)
        for _ in range(CARDS_PER_ROUND):
            round.add_card(game_deck.pick_card())
        round.rand_face_up()
        print('Cards:\n', round.show_round(), '\n')

        # print('EV =', round.calculate_ev(),'\n')
        
        # Market maker quotes
        bid, ask = round.calculate_spread()
        print(f'Market maker quotes {bid} at {ask}\n')
        
        if SHOW_BALANCE:
            print('Balance: ', player.balance)
        
        # Player trades
        print('Buy (B) / Sell (S) / Pass (P) followed by how many units e.g. B,10 or S,5')
        while True:
            user_in = input('Place order >>> ').split(',')
            # TODO: Input validation

            if user_in[0].lower() == 'b' and len(user_in) > 1:
                round.place_order('Buy', int(user_in[1]))
                break
            elif user_in[0].lower() == 's' and len(user_in) > 1:
                round.place_order('Sell', int(user_in[1]))
                break
            elif user_in[0].lower() == 'p':
                round.place_order('Pass', 0)
                break
            else:
                print("Invalid input")
            

        # Reveal true market price
        print('\nCard Reveal')
        print(''.join([f'{str(card):<4}' for card in round.picked_cards]),'\n')


        # Player reports P/L
        if round.order != 'Pass':
            print('Enter profit/loss (-ve is loss)')
            while True:
                user_in = input('>>> ')
                if user_in.isnumeric():
                    user_in = int(user_in)
                    break
 
        round.calculate_pl()
        player.balance += round.player_true_pl
        if SHOW_BALANCE:
            print('Balance: ', player.balance)

        game_rounds.append(copy.deepcopy(round))
        round.clear_cards()

    print('Game summary')
    for r in game_rounds:
        print(str(r), '\n')
        


if __name__ == '__main__':
    main()


