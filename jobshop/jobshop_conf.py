# coding=utf-8
# -*- coding: utf-8 -*-
import logging

from genetic_classes import *
from pyage.core import address
from pyage.jobshop.agents import masters_factory, slaves_factory
from pyage.core.stop_condition import StepLimitStopCondition
from pyage.jobshop.problemGenerator import  ProblemGenerator, UniformIntDistribution, RandomizedTasksProvider, PredictedProblemGenerator, RandomizedProblemProvider
from pyage.jobshop.statistics import  GanttStatistics
from pyage.jobshop.timeKeeper import TimeKeeper
from pyage.jobshop.manufacture import Manufacture


logger = logging.getLogger(__name__)
agents_count = 1
jobshop_agents = 3
machines_number = 3
logger.debug("AGGREGATE, %s agents", agents_count)

seed = None

timeKeeper = lambda: TimeKeeper(5,-1)
manufacture = lambda: Manufacture(machines_number)

start_problem_provider = RandomizedProblemProvider(
				jobs_number = 20,
				job_duration_distrib = UniformIntDistribution(17,28),
				tasks_number_distrib = UniformIntDistribution(1,3),
				tasks_provider = RandomizedTasksProvider(machines_number)
				,seed = seed
			)
predicted_problem_provider = RandomizedProblemProvider(
				jobs_number = 1,
				job_duration_distrib = UniformIntDistribution(1,1),
				tasks_number_distrib = UniformIntDistribution(1,1),
				tasks_provider = RandomizedTasksProvider(machines_number)
				,seed = seed
			)

incomming_problem_provider = RandomizedProblemProvider(
				jobs_number = 1,
				job_duration_distrib = UniformIntDistribution(2,4),
				tasks_number_distrib = UniformIntDistribution(1,3),
				tasks_provider = RandomizedTasksProvider(machines_number)
				,seed = seed
			)

problemGenerator = lambda: ProblemGenerator(50, start_problem_provider, incomming_problem_provider)

predictedProblemGenerator = lambda: PredictedProblemGenerator(predicted_problem_provider, jobshop_agents)

agents = masters_factory(agents_count)
slaves = slaves_factory(jobshop_agents)

stop_condition = lambda: StepLimitStopCondition(1000)

evaluation = lambda: BasicJobShopEvaluation(machines_number)
selection = lambda: BasicJobShopSelection()
mutation = lambda: GreaterJobShopMutation()

address_provider = address.SequenceAddressProvider

stats = GanttStatistics
