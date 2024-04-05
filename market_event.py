"""
Alson Lee
Date: 05/04/24

The market_event module contains methods for market events.
"""
from collections import deque
import random as rand

from deck import Deck

"""
Class to represent a deck restriction market event.
"""
class EventDeckRestriction:
    def __init__(self, description='', 
                 restrict_card_ranks = [], 
                 restrict_card_suits = []) -> None:
        self.description = description
        self.restrict_card_ranks = restrict_card_ranks
        self.restrict_card_suits = restrict_card_suits


"""
Class to represent a card modifier market event.
"""
class EventCardModifier:
    def __init__(self, description='', 
                 modify_card_value={}) -> None:
        self.description = description
        self.modify_card_value = modify_card_value


"""
Class to represent a market event.
"""
class MarketEvent:
    PRESET_EVENTS = {100: EventDeckRestriction('Odd card values only'),
                     101: EventDeckRestriction('Even card values only'),
                     110: EventDeckRestriction('These suits only'),
                     120: EventDeckRestriction('Card value X or less only'),
                     121: EventDeckRestriction('Card value X or more only'),
                     200: EventCardModifier('Card X is now worth Y'),
                     201: EventCardModifier('Even cards are now worth double'),
                     202: EventCardModifier('Odd cards are now worth double')}

    def __init__(self, event_id=0, event_chance=0.5, 
                 deck=None) -> None:
        self.event_id = event_id
        self.event_data = None
        self.event_chance = event_chance
        self.deck: deque = deck

    def get_event(self):
        pass

    def random_event(self):
        if rand.random() < self.event_chance:
            self.event_id = rand.choice(list(self.PRESET_EVENTS.keys()))
            self.event_data = self.PRESET_EVENTS[self.event_id]

    def get_even_value_cards(self):
        pass

    def get_odd_value_cards(self):
        pass

    def get_mod_value_cards(self):
        pass