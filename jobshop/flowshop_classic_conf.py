# coding=utf-8
import logging

from pyage.core import address
from pyage.core.agent.agent import generate_agents, Agent
from pyage.core.locator import RandomLocator
from pyage.core.migration import NoMigration
from pyage.core.stats.statistics import SchedulingProblemStatistics
from pyage.core.stop_condition import TimeLimitStopCondition
from pyage.solutions.evolution.crossover.permutation import FirstHalfSwapsCrossover
from pyage.solutions.evolution.evaluation import FlowShopEvaluation
from pyage.solutions.evolution.initializer import PermutationInitializer
from pyage.solutions.evolution.mutation import PermutationMutation
from pyage.solutions.evolution.selection import TournamentSelection


time_matrix = lambda: [
    [54, 83, 15, 71, 77, 36, 53, 38, 27, 87, 76, 91, 14, 29, 12, 77, 32, 87, 68, 94],
    [79, 3, 11, 99, 56, 70, 99, 60, 5, 56, 3, 61, 73, 75, 47, 14, 21, 86, 5, 77],
    [16, 89, 49, 15, 89, 45, 60, 23, 57, 64, 7, 1, 63, 41, 63, 47, 26, 75, 77, 40],
    [66, 58, 31, 68, 78, 91, 13, 59, 49, 85, 85, 9, 39, 41, 56, 40, 54, 77, 51, 31],
    [58, 56, 20, 85, 53, 35, 53, 41, 69, 13, 86, 72, 8, 49, 47, 87, 58, 18, 68, 28]
]
JOBS_COUNT = len(time_matrix()[0])
AGENTS_COUNT = 50
POPULATION_SIZE = 20

agents = generate_agents("flowshop", AGENTS_COUNT, Agent)
stop_condition = lambda: TimeLimitStopCondition(10)

evaluation = lambda: FlowShopEvaluation(time_matrix())
initializer = lambda: PermutationInitializer(JOBS_COUNT, POPULATION_SIZE)
operators = lambda: [
    FirstHalfSwapsCrossover(),
    PermutationMutation(2),
    evaluation(),
    TournamentSelection(POPULATION_SIZE, POPULATION_SIZE)]

address_provider = address.SequenceAddressProvider

migration = NoMigration
locator = RandomLocator

stats = lambda: SchedulingProblemStatistics('out_%s_pyage.txt' % __name__)
logger = logging.getLogger(__name__)
logger.debug("Classic, %s agents", AGENTS_COUNT)
