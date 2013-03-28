# coding=utf-8
import os
import Pyro4

from pyage.core import address
from pyage.core.agent import  agents_factory, generate_agents, AggregateAgent
from pyage.core.locator import  ParentLocator
from pyage.core.migration import Pyro4Migration
from pyage.core.statistics import SimpleStatistics
from pyage.solutions.evolution.crossover import  AverageFloatCrossover
from pyage.solutions.evolution.evaluation import  FloatRastriginEvaluation
from pyage.solutions.evolution.initializer import  FloatInitializer
from pyage.solutions.evolution.mutation import  UniformFloatMutation
from pyage.solutions.evolution.selection import TournamentSelection

agents = generate_agents("agent", int(os.environ['AGENTS']), AggregateAgent)
aggregated_agents = agents_factory("max", "makz", "m", "a")
step_limit = lambda: 1000

size = 1000
operators = lambda: [FloatRastriginEvaluation(), TournamentSelection(size=150, tournament_size=150),
                     AverageFloatCrossover(size=size), UniformFloatMutation(probability=0.1, radius=1)]
initializer = lambda: FloatInitializer(10, size, -10, 10)

address_provider = address.AddressProvider

migration = Pyro4Migration
locator = ParentLocator

ns_hostname = lambda: os.environ['NS_HOSTNAME']
pyro_daemon = Pyro4.Daemon()
daemon = lambda: pyro_daemon

stats = SimpleStatistics