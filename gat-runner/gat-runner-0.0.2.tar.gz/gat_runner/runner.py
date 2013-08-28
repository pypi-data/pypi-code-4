# coding: utf-8
import logging

import random

from gat_games.game_engine.engine import GATLogger
from gat_games.games import *
from gat_runner.languages import GATFileFactory
# Important to update all Game.Player references
from gat_runner.players import *


def play_gat(Game, seed, players, log_level=logging.INFO, player_log=False):
    GATLogger.set_level(log_level)
    for player in players:
        player.start(player_log=player_log)
    if not seed:
        seed = random.randint(1, 9999999)
    game = Game(seed, players)
    game.start()
    game.print_summary()

    for player in players:
        player.stop()
    return game


def play_random_algorithm_vs_random_algorithm(Game, seed, name1=None, name2=None, log_level=logging.INFO):
    players = [Game.RandomStrategy(name=name1), Game.RandomStrategy(name=name2)]
    return play_gat(Game, seed, players, log_level=log_level)


def play_native_algorithm_vs_random_algorithm(Game, seed, custom_strategy, log_level=logging.INFO):
    players = [Game.RandomStrategy(), custom_strategy]
    return play_gat(Game, seed, players, log_level=log_level)


def play_file_against_random_algorithm(Game, seed, filepath, language=None, name1=None, name2=None, log_level=logging.INFO):
    gat_file = GATFileFactory.create(filepath, language=language)
    gat_file.compile()
    command = gat_file.get_runtime_command()
    player1 = Game.Player(command, name=name1)

    player2 = Game.RandomStrategy(name=name2)

    return play_gat(Game, seed, [player1, player2], log_level=log_level)


def play_file_against_file(Game, seed, filepath1, filepath2, language1=None, language2=None, name1=None, name2=None, log_level=logging.INFO):
    gat_file1 = GATFileFactory.create(filepath1, language=language1)
    gat_file1.compile()
    command1 = gat_file1.get_runtime_command()
    player1 = Game.Player(command1, name=name1)

    gat_file2 = GATFileFactory.create(filepath2, language=language2)
    gat_file2.compile()
    command2 = gat_file2.get_runtime_command()
    player2 = Game.Player(command2, name=name2)

    return play_gat(Game, seed, [player1, player2], log_level=log_level)


def play_from_command_line(Game, seed, filepath1='gat-random', filepath2='gat-random', language1=None, language2=None, name1=None, name2=None, log_level=logging.INFO, player_log=False):
    if filepath1 == 'gat-random':
        player1 = Game.RandomStrategy(name=name1)
    else:
        gat_file1 = GATFileFactory.create(filepath1, language=language1)
        gat_file1.compile()
        command1 = gat_file1.get_runtime_command()
        player1 = Game.Player(command1, name=name1)

    if filepath2 == 'gat-random':
        player2 = Game.RandomStrategy(name=name2)
    else:
        gat_file2 = GATFileFactory.create(filepath2, language=language2)
        gat_file2.compile()
        command2 = gat_file2.get_runtime_command()
        player2 = Game.Player(command2, name=name2)

    return play_gat(Game, seed, [player1, player2], log_level=log_level, player_log=player_log)
