"""
Alson Lee
Date: 17/03/24

The deck module contains methods for cards and decks for the 
market making card game.
"""

import random as rand

"""
Class to represent a playing card.
"""
class Card:
    def __init__(self, card_id=0, rank=0, suit=None) -> None:
        self.card_id: int = card_id
        self.rank: int = rank
        self.suit: str = suit

    def __str__(self) -> str:
        return f'{self.rank}{self.suit}'


"""
Class to represent a deck of cards.
"""
class Deck:
    def __init__(self, ranks=None, suits=None) -> None:
        if suits is None:
            suits = []
        if ranks is None:
            ranks = []
        self.ranks: list[str] = ranks
        self.suits: list[str] = suits

        self.deck: list = []
        if len(self.deck) == 0:
            self.create_deck(self.ranks, self.suits)

    def __str__(self) -> str:
        return ', '.join([str(card) for card in self.deck])

    def create_deck(self, ranks: list[str], suits: list[str]) -> None:
        """
        Creates a representation of a deck of cards with suits and values.
        :param suits:  The list of suits
        :param values: The list of values
        :return:       Representation of a deck as list
        """
        card_id = 0
        new_deck = []
        if ranks and suits:
            for rank in ranks:
                for suit in suits:
                    new_deck.append(Card(card_id, rank, suit))
                    card_id += 1
            self.deck = new_deck
        else:
            print("Cannot create deck!")

    def shuffle(self) -> None:
        """
        Shuffles deck of cards with Fisher-Yates algorithm
        :param deck:  Representation of a deck as list
        :return:      The shuffled deck as list
        """
        # Shuffle the deck with Fisher–Yates algorithm
        if len(self.deck) > 1:
            for i in range(len(self.deck) - 1):
                j = rand.randint(i, len(self.deck) - 1)
                self.deck[i], self.deck[j] = self.deck[j], self.deck[i]

    def pick_card(self) -> Card:
        """
        Return the card from the top of the deck.
        :return:     A card from the deck
        """
        return self.deck.pop(rand.randint(0, len(self.deck) - 1)) if len(
            self.deck) > 0 else None
