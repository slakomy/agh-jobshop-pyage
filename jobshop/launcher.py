from pyage.core.stop_condition import get_all_jobs_scheduled_stop_condition, AllJobsScheduledStopCondition
from flowshop_genetics import PermutationInitializer, FirstHalfSwapsCrossover, PermutationMutation
from flowshop_genetics import FlowShopEvaluation
from manufacture import Manufacture
from pyage.jobshop.problemGenerator import ProblemProvider
from timeKeeper import TimeKeeper
from statistics import GanttStatistics
from agents import masters_factory
import logging

import launcher_config_small as l_conf
from pyage.core import inject
from pyage.core.address import SequenceAddressProvider
from pyage.core.agent.agent import generate_agents, Agent
from pyage.core.locator import RandomLocator
from pyage.core.migration import NoMigration
from pyage.core.workplace import Workplace
from pyage.solutions.evolution.selection import TournamentSelection


logger = logging.getLogger(__name__)

all_jobs_scheduled_stop_condition = AllJobsScheduledStopCondition()


def get_all_jobs_scheduled_stop_condition():
    return all_jobs_scheduled_stop_condition


def main():
    for incoming_problem in l_conf.incoming_problems:
        for obj in l_conf.matrices:
            print "Initial problem matrix: {0}\nIncoming problem matrices: {1}".format(obj, incoming_problem)
            for number_of_aggregates in l_conf.numbers_of_aggregates:
                msg = "agents: {0}, population_size: {1}".format(number_of_aggregates,
                                                                 l_conf.aggregate_sizes)
                # print msg
                for i in xrange(l_conf.repeats):
                    logger.info(msg)
                    lunch_computation(number_of_aggregates, l_conf.aggregate_sizes, obj, incoming_problem)


def create_base_params():
    return {
        "stop_condition": lambda: get_all_jobs_scheduled_stop_condition(),
        "locator": RandomLocator,
        "logger": lambda: logger,
        "address_provider": lambda: SequenceAddressProvider(),
        "stats": lambda: GanttStatistics()
    }


def create_resolver(params):
    def resolver(conf, conf_arg_name, args):
        try:
            return params[args[0].address.split('.')[0] + '__' + conf_arg_name]()
        except:
            return params[conf_arg_name]()

    return resolver


def create_classic_params(agents_count, agent_population, time_matrix, incoming_problems_feed):
    JOBS_COUNT = len(time_matrix[0])
    return {
        "agents": masters_factory(1, l_conf.window_time, time_matrix, l_conf.distortion_factor),
        "manufacture": lambda: Manufacture(len(time_matrix)),
        "timeKeeper": lambda: TimeKeeper(1, 1),
        "slaves": generate_agents("flowshop", agents_count, Agent),
        "initializer": lambda: PermutationInitializer(JOBS_COUNT, agent_population),
        "evaluation": lambda: FlowShopEvaluation(time_matrix),
        "operators": lambda: [
            FirstHalfSwapsCrossover(),
            PermutationMutation(2),
            FlowShopEvaluation(time_matrix),
            TournamentSelection(agent_population, agent_population)
        ],
        "migration": NoMigration,
        "problem_provider": lambda: ProblemProvider(incoming_problems_feed)
    }


def lunch_computation(agents_count, agent_population, obj, incoming_problems_feed):
    base_params = create_base_params()
    specific_params = create_classic_params(agents_count, agent_population, obj["matrix"], incoming_problems_feed)

    inject.resolve_attr = create_resolver(dict(base_params.items() + specific_params.items()))

    workplace = Workplace()
    workplace.publish()
    while not workplace.stopped:
        workplace.step()
    workplace.unregister()


if __name__ == "__main__":
    level = logging.INFO
    # logging.basicConfig(level=level)
    main()