"""
Alson Lee
Date: 05/04/24

Market making card game
"""
import copy
from itertools import permutations
import numpy as np
import matplotlib.pyplot as plt
import os

import random as rand
from deck import Card, Deck
from market_event import MarketEvent

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

"""
Class to represent a round of the market making card game.
"""
class Round:
    def __init__(self, round_num=1, const_deck=None, picked_cards=[],
                 is_face_up=[], card_values={}, seen_cards=set(), 
                 market_events_enabled=False) -> None:
        self.round_num: int = round_num
        self.const_deck: Deck = const_deck
        self.card_values: dict[str, int] = card_values

        self.picked_cards: list[Card] = picked_cards
        self.is_face_up: list[bool] = is_face_up
        self.seen_cards: set[Card] = seen_cards
        self.ev: float = 0

        self.order = None
        self.order_unit = 0
        self.spread = ()

        self.player_start_bal = 0
        self.player_end_bal = 0
        self.player_true_pl = 0
        self.player_input_pl = 0

        self.market_events_enabled = market_events_enabled
        self.market_event: MarketEvent = None 

    def __str__(self) -> str:
        return (  f'Round:         {self.round_num}' + '\n'
                + f'Cards:         {self.show_round()} (EV = {self.ev:.2f})' + '\n'
                + f'Reveal:        {self.reveal_all_cards()} (Actual = {self.sum_value()})' + '\n'
                + f'Spread:        {self.spread[0]} at {self.spread[1]}' + '\n'
                + f'Order:         {self.order} {self.order_unit if self.order_unit > 0 else ""}' + '\n'
                + f'P/L reported:  {self.player_input_pl}' + '\n'
                + f'P/L actual:    {self.player_true_pl}' + '\n'
                + f'Start balance: {self.player_start_bal}' + '\n'
                + f'End balance:   {self.player_end_bal}')

    def show_round(self, face_down_sym: str = '--') -> str:
        """
        Returns a string of the round for the player.
        :param face_down_sym: The symbol if the card is face-down. Default is --.
        :return: String of cards. By default, -- if the card is face-down.
        """
        show = []
        for card, is_face_up in zip(self.picked_cards, self.is_face_up):
            if is_face_up:
                show.append(f'{str(card):<4}')
                self.seen_cards.add(card.card_id)
            else:
                show.append(f'{face_down_sym:<4}')
        return ''.join(show)

    def reveal_all_cards(self) -> str:
        """
        Returns a string of all cards.
        :return: String of all cards.
        """
        reveal = []
        for card in self.picked_cards:
            self.seen_cards.add(card.card_id)
            reveal.append(f'{str(card):<4}')
        return ''.join(reveal)

    def rand_face_up(self) -> None:
        """
        Randomly assigns cards in a round to be face-up (True) or face-down (False).
        """
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
        """
        Calculates the EV given any revealed cards. 
        :return: The EV given any revealed cards.
        """
        # Calculate sum of values for any cards which have not been seen.
        value_sum = 0
        for card in self.const_deck.deck:
            card: Card
            if card.card_id not in self.seen_cards:
                value_sum += self.card_values[card.rank]

        # Calculate EV of which have not been seen.
        total_cards = len(self.const_deck.ranks) * len(self.const_deck.suits)
        ev_unseen = value_sum / (total_cards - len(self.seen_cards))

        ev = 0
        for card, is_face_up in zip(self.picked_cards, self.is_face_up):
            if is_face_up:
                ev += self.card_values[card.rank]
            else:
                ev += ev_unseen
        self.ev = ev
        return ev

    def calculate_max_value(self) -> int:
        """
        Calculates the max possible total value given any revealed cards. 
        Used to check if short positions will exceed the current balance.
        :return: The max total value given any revealed cards.
        """
        # Sort deck by value
        sort_deck: list[Card] = sorted(self.const_deck.deck,
                                       key=lambda card: self.card_values[card.rank])
        # Remove any seen cards
        for card in sort_deck:
            card: Card
            if card.card_id in self.seen_cards:
                sort_deck.remove(card)

        # Calculate max value picking from the highest value card then 
        # 2nd highest, 3rd highest etc.
        max_val = 0
        idx = -1
        for card, is_face_up in zip(self.picked_cards, self.is_face_up):
            if is_face_up:
                max_val += self.card_values[card.rank]
            else:
                max_val += self.card_values[sort_deck[idx].rank]
                idx -= 1

        return max_val

    def sum_value(self) -> int:
        """
        Calculates the total value of the cards including unrevealed cards.
        :return: The total value of the cards
        """
        total = 0
        for card in self.picked_cards:
            total += self.card_values[card.rank]
        return total

    def calculate_spread(self) -> tuple:
        """
        Generates a spread for the round given the EV of the current round.
        :return: Tuple (bid,ask) price
        """
        offset_limit = int(self.ev / 5)
        offset = rand.randint(-offset_limit, offset_limit)

        spread_width = rand.randint(2, 6)
        spread_bid = self.ev + offset - spread_width // 2
        spread_ask = self.ev + offset + spread_width // 2
        self.spread = int(spread_bid), int(spread_ask)
        return self.spread

    def calculate_pl(self) -> int:
        """
        Calculates the profit/loss for the round given the player's 
        order and the current spread.
        :return: The profit/loss for the round (negative values is loss)
        """
        if self.order == 'Buy':
            pl = (self.sum_value() - self.spread[1]) * self.order_unit
        elif self.order == 'Sell':
            pl = (self.spread[0] - self.sum_value()) * self.order_unit
        else:
            pl = 0
        self.player_true_pl = pl
        return self.player_true_pl

    def calculate_value_distribution(self) -> None:
        """
        Generates the distribution of values given any revealed cards and saves 
        the histogram to file.
        """
        # Sum face_up cards
        sum_face_up = 0
        for card, is_face_up in zip(self.picked_cards, self.is_face_up):
            if is_face_up:
                sum_face_up += self.card_values[card.rank]

        # Remove any seen cards
        not_seen = list(copy.deepcopy(self.const_deck.deck))
        for card in not_seen:
            card: Card
            if card.card_id in self.seen_cards:
                not_seen.remove(card)
        
        # Get permutations
        face_down = len(self.picked_cards) - sum(self.is_face_up)
        perms = permutations(not_seen, face_down)

        # Frequency of values
        frequency = []
        for card_perm in perms:
            val = 0
            for card in card_perm:
                val += self.card_values[card.rank]
            val += sum_face_up
            frequency.append(val)
        
        # Plot and save
        _path = f'{DIR_PATH}/charts/round_{self.round_num}_histogram.png'
        num_bins = len(set(frequency))
        fig, ax = plt.subplots()
        ax.hist(frequency, num_bins, density=True)
        ax.set_xlabel('Value')
        ax.set_xlim(xmin=0, xmax=50)
        ax.set_ylabel('Probability Density')
        ax.set_ylim(ymax=0.1)
        ax.set_title(f'Card Value Sum Probability Density - Round {self.round_num}')
        fig.tight_layout()
        try:
            plt.savefig(_path, bbox_inches="tight")
        except FileNotFoundError:
            pass

    def check_order(self, order: str, units: int) -> bool:
        """
        Checks if an order is valid which is limited by the player balance.
        :param order: The order type 'Buy' or 'Sell'
        :param units: The number of units for the order
        :return:      Valid (True) or not valid (False)
        """
        if order == 'Buy':
            # Check if valid long position
            if self.spread[1] * units <= self.player_start_bal:
                return True
        elif order == 'Sell':
            # Check if valid short position
            if ((self.calculate_max_value() - self.spread[0]) * units 
                    <= self.player_start_bal):
                return True
        return False

    def place_order(self, order: str, units: int) -> bool:
        """
        Places an order.
        :param order: The order type 'Buy', 'Sell' or 'Pass'
        :param units: The number of units for the order if 'Buy' or 'Sell'
        :return:      Success (True) or Fail (False)
        """
        if order == 'Pass':
            self.order = order
            return True
        if self.check_order(order, units):
            self.order = order
            self.order_unit = units
            return True
        return False

    def add_card(self, card: Card) -> None:
        """
        Adds a card to the round in face-down by default.
        :param card: The card to be added.
        """
        self.picked_cards.append(card)
        self.is_face_up.append(False)

    def clear_cards(self) -> None:
        """
        Clears the cards and card states for the round.
        """
        self.picked_cards.clear()
        self.is_face_up.clear()

    def roll_market_event(self) -> int:
        if self.market_events_enabled:
            event = MarketEvent()

        else:
            return 0
        