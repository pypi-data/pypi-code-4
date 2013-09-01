"""
Tests for `librarian.card` module.
"""
import pytest
from librarian.card import Card


class TestCard(object):

    def test_constructor(self):
        card = Card(1, 'Test')

        assert card.code == 1
        assert card.name == 'Test'
        assert card.abilities == {}
        assert card.attributes == []
        assert card.info == {}

    def test_is_valid(self):
        card = Card(1, 'Test')
        assert card.is_valid() is True

        card.code = 0
        assert card.is_valid() is False

        card.code = 1
        card.name = ''
        assert card.is_valid() is False

    def test_has_attribute(self):
        card = Card()
        card.add_attribute('test')

        assert card.has_attribute('test') is True
        assert card.has_attribute('card') is False

    def test_add_attribute(self):
        card = Card()
        card.add_attribute('test')
        assert card.has_attribute('test') is True

    def test_get_abilities(self):
        card = Card()
        card.add_ability('attack', 'Facepalm')

        assert card.get_abilities('block') is None
        assert card.get_abilities('attack') == ['Facepalm']

    def test_add_ability(self):
        card = Card()

        assert card.add_ability('attack', 'Facepalm')
        assert 'Facepalm' in card.get_abilities('attack')
        assert card.add_ability('attack', 'Slap')
        assert 'Slap' in card.get_abilities('attack')

    def test_get_info(self):
        card = Card()
        card.set_info('description', 'For testing.')

        assert card.get_info('art') is None
        assert card.get_info('description')[0] == 'For testing.'

    def test_set_info(self):
        card = Card()
        card.set_info('description', 'For testing.')
        card.set_info('art', 1, True)
        card.set_info('art', 2)

        assert card.get_info('description')[0] == 'For testing.'
        assert 1 in card.get_info('art')
        assert 2 in card.get_info('art')

    def test_save_load(self):
        original = Card(1, 'Test')
        original.add_ability('attack', 'Slap')
        original.add_attribute('test')
        original.set_info('art', 1)
        savedict = original.save()
        loaded = Card(loaddict=savedict)

        assert loaded.code == original.code
        assert loaded.name == original.name
        assert loaded.abilities == original.abilities
        assert loaded.attributes == original.attributes
        assert loaded.info == original.info

    def test_equality(self):
        card1 = Card(1)
        card2 = Card(2)
        card3 = Card(1)

        assert card1 != card2
        assert card1 == card3

    def test_representation(self):
        card = Card(12345)

        assert repr(card) == '<Card:12345>'
