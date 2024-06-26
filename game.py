"""
Alson Lee
Date: 05/04/24

Market making card game
"""

import copy
import random as rand
import time
import threading
import re

import display
from round import Round
from deck import Card, Deck
from player import Player

"""
Game settings
"""
CARDS_PER_ROUND = 3
ROUNDS = 3
TIME_LIMIT = 60

MARKET_EVENTS = False
MARKET_EVENT_CHANCE = 0.5

START_BALANCE = 500
SHOW_BALANCE = True

SUITS = {1: ['♥', '♦', '♣', '♠'],
         2: ['🐄', '🐍', '🐕', '🐬', '🐞'],
         3: ['⚽', '⭐', '❌', '🔶', '✅', '♒', '🔵']}

RANKS = {1: list(map(str, range(2, 11))) + ['J', 'Q', 'K', 'A'],
         2: list(map(str, range(1, 21))),
         3: list(map(str, range(1, 31)))}

FACE_CARD_VALUES = {1: {'J': 11, 'Q': 12, 'K': 13, 'A': 14}, 
                    2: {'A': 1, 'J': 11, 'Q': 12, 'K': 13}}

# TODO: Timer
class Timer:
    def __init__(self, turn_time = 0) -> None:
        self.turn_time = turn_time


def main() -> None:
    display.print_title()

    ranks, suits, face_card_values = RANKS[1], SUITS[1], FACE_CARD_VALUES[1]

    display.show_settings(cards_per_round=CARDS_PER_ROUND, rounds=ROUNDS, 
                          time_limit=TIME_LIMIT, market_events=MARKET_EVENTS, 
                          start_balance=START_BALANCE, show_balance=SHOW_BALANCE)
    display.show_card_values(suits, ranks, face_card_values)
    values = {}
    for rank in ranks:
        if rank.isnumeric():
            values[rank] = int(rank)
        else:
            values[rank] = face_card_values[rank]

    display.print_instructions()

    # Instantiate deck and player
    game_deck = Deck(ranks, suits)
    game_deck.shuffle()
    player = Player(START_BALANCE)

    round_history: list[Round] = []  # History of rounds

    curr_round = 1  # Round number
    while curr_round <= ROUNDS and len(game_deck.deck) > 0:
        display.print_divider()
        print(f'Round {curr_round}', '\n')

        # Create round and pick cards
        round = Round(round_num=curr_round, const_deck=Deck(ranks, suits), card_values=values)
        for _ in range(CARDS_PER_ROUND):
            card = game_deck.pick_card()
            if card:
                round.add_card(card)
        round.rand_face_up()
        print('Cards this round:\n', round.show_round(), '\n', sep='')
        round.calculate_ev()
        round.calculate_value_distribution()
        # print('EV =', f'{round.ev:.2f}','\n')
        
        # Market maker quotes
        bid, ask = round.calculate_spread()
        print(f'Market maker quotes {bid} at {ask}\n')
        
        if SHOW_BALANCE:
            print('Balance: ', player.balance)
        round.player_start_bal = player.balance
        
        # Player trades
        print('Buy (B) / Sell (S) / Pass (P) followed by how many units e.g. B,10 or S,5')
        while True:
            user_in = input('Place order >>> ')
            if user_in.lower().strip() == 'p':
                round.place_order('Pass', 0)
                break

            match = re.match(r'[bs][,][1-9]\d*', user_in)
            if match:
                action, units = match.group().split(',')
                if action.lower() == 'b':
                    if round.place_order('Buy', int(units)):
                        break
                    print('Long position exceeds balance')
                elif action.lower() == 's':
                    if round.place_order('Sell', int(units)):
                        break
                    print('Short position exceeds balance')
            else:
                print("Invalid input")
            
        # Reveal true market price
        print('\nCard Reveal')
        print(round.reveal_all_cards(),'\n')

        # Player reports P/L
        if round.order != 'Pass':
            print('Enter profit/loss (-ve is loss)')
            while True:
                user_in = input('>>> ')
                match = re.match(r'[-]?[1-9]+\d*', user_in)
                if match:
                    round.player_input_pl = int(match.group())
                    break
                else:
                    print("Invalid input")

        # Check true P/L
        round.calculate_pl()
        player.balance += round.player_true_pl
        round.player_end_bal = player.balance
        if SHOW_BALANCE:
            print('Balance: ', player.balance)

        # Append a copy of the round to the round history
        round_history.append(copy.deepcopy(round))
        round.clear_cards()
        curr_round += 1

    # Display post-game summary
    display.print_divider()
    print('Game summary')
    for round in round_history:
        print(str(round), '\n')
        

if __name__ == '__main__':
    main()


