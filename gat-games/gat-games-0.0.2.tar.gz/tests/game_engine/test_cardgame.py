# coding: utf-8
import unittest

from gat_games.game_engine.cardgame import *


class CardTests(unittest.TestCase):
    def test_valid_card(self):
        card = Card(AS, SPADES)
        self.assertEquals(SPADES, card.suit)
        self.assertEquals(AS, card.rank)

    def test_card_validate_rank(self):
        try:
            Card(999, SPADES)
            self.assertFalse(True)
        except AttributeError as e:
            self.assertEquals('Invalid card rank', str(e))

    def test_card_validate_suit(self):
        try:
            Card(AS, 999)
            self.assertFalse(True)
        except AttributeError as e:
            self.assertEquals('Invalid card suit', str(e))

    def test_cards_print_niceley(self):
        self.assertEquals('AS-1', str(Card(AS, SPADES)))
        self.assertEquals('J-1', str(Card(J, SPADES)))
        self.assertEquals('5-1', str(Card(5, SPADES)))

    def test_cards_are_ordered_by_rank(self):
        self.assertEquals(True, Card(2, SPADES) > Card(1, SPADES))
        self.assertEquals(False, Card(2, SPADES) > Card(2, SPADES))

        self.assertEquals(True, Card(2, SPADES) >= Card(1, SPADES))
        self.assertEquals(True, Card(2, SPADES) >= Card(2, SPADES))
        self.assertEquals(False, Card(2, SPADES) >= Card(3, SPADES))

        self.assertEquals(True, Card(1, SPADES) < Card(2, SPADES))
        self.assertEquals(False, Card(2, SPADES) < Card(2, SPADES))

        self.assertEquals(True, Card(1, SPADES) <= Card(2, SPADES))
        self.assertEquals(True, Card(2, SPADES) <= Card(2, SPADES))
        self.assertEquals(False, Card(3, SPADES) <= Card(2, SPADES))

    def test_cards_are_compared(self):
        self.assertEquals(True, Card(2, SPADES) == Card(2, SPADES))
        self.assertEquals(False, Card(2, SPADES) == Card(3, SPADES))

        self.assertEquals(True, Card(2, SPADES) != Card(3, SPADES))
        self.assertEquals(False, Card(2, SPADES) != Card(2, SPADES))

    def test_cards_can_be_included_in_sets(self):
        cards = set()
        cards.add(Card(AS, SPADES))
        cards.add(Card(2, SPADES))
        cards.add(Card(2, SPADES))
        self.assertEquals(2, len(cards))


class DeckTests(unittest.TestCase):
    def setUp(self):
        self.deck = Deck()

    def test_len(self):
        self.assertEquals(0, len(self.deck))

    def test_count(self):
        self.assertEquals(0, self.deck.count())

    def test_deck_print_niceley(self):
        self.deck.push(Card(AS, SPADES))
        self.assertEquals('AS-1', str(self.deck))
        self.deck.push(Card(5, SPADES))
        self.assertEquals('AS-1,5-1', str(self.deck))

    def test_build(self):
        self.assertEquals(0, len(self.deck))
        self.deck.build()
        self.assertEquals(13*4, len(self.deck))

    def test_build_rebuild(self):
        self.deck.build()
        self.deck.pop()
        self.deck.build()
        self.assertEquals(13*4, len(self.deck))

    def test_push(self):
        self.deck.push(1)
        self.assertEquals(1, len(self.deck))

    def test_see(self):
        self.deck.push(Card(AS, SPADES))
        self.assertEquals('AS-1', str(self.deck.see(0)))

    def test_pop(self):
        self.deck.push(9)
        result = self.deck.pop()
        self.assertEquals(9, result)
        self.assertEquals(0, len(self.deck))

    def test_remove(self):
        self.deck.push(9)
        result = self.deck.remove(9)
        self.assertEquals(9, result)
        self.assertEquals(0, len(self.deck))

    def test_clear(self):
        self.deck.push(9)
        self.deck.push(99)
        self.deck.clear()
        self.assertEquals(0, len(self.deck))

    def test_pop_with_index(self):
        self.deck.push(9)
        self.deck.push(99)
        self.deck.push(999)
        result = self.deck.pop(1)
        self.assertEquals(99, result)
        self.assertEquals(2, len(self.deck))

    def test_shuffle(self):
        pass

    def test_sort(self):
        pass

    def test_distribute(self):
        self.deck.build()
        decks = [Deck(), Deck()]
        self.deck.distribute(decks, 5)
        self.assertEquals(13*4 - 10, len(self.deck))
        self.assertEquals(5, len(decks[0]))
        self.assertEquals(5, len(decks[1]))


class CardGameRoundTests(unittest.TestCase):
    def test_deck(self):
        pass

    def test_hands(self):
        game = CardGameRound(0, [])
        self.assertEquals(0, len(game.hands))

        game = CardGameRound(0, [Player()])
        self.assertEquals(1, len(game.hands))