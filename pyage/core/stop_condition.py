import logging
import Pyro4
from pyage.core.inject import Inject
from pyage.core.workplace import WORKPLACE

class StopCondition(object):
    def should_stop(self, workplace):
        raise NotImplementedError()


class StepLimitStopCondition(StopCondition):
    def __init__(self, step_limit):
        super(StepLimitStopCondition, self).__init__()
        self.step_limit = step_limit

    def should_stop(self, workplace):
        return 0 < self.step_limit <= workplace.steps


class AllJobsScheduledStopCondition(StopCondition):
    def __init__(self):
        self.__all_jobs_scheduled = False

    def should_stop(self, workplace):
        return self.__all_jobs_scheduled

    def set_all_jobs_scheduled(self, value):
        self.__all_jobs_scheduled = value


all_jobs_scheduled_stop_condition = AllJobsScheduledStopCondition()

def get_all_jobs_scheduled_stop_condition():
    return all_jobs_scheduled_stop_condition


class MinimumFitnessStopCondition(StopCondition):
    def __init__(self, minimal_fitness):
        super(MinimumFitnessStopCondition, self).__init__()
        self.minimal_fitness = minimal_fitness

    def should_stop(self, workplace):
        return workplace.get_fitness() >= self.minimal_fitness


class GlobalMinimumFitnessStopCondition(StopCondition):
    @Inject("ns_hostname")
    def __init__(self, minimal_fitness):
        super(GlobalMinimumFitnessStopCondition, self).__init__()
        self.minimal_fitness = minimal_fitness

    def should_stop(self, workplace):
        try:
            fitness = workplace.get_fitness()
            if fitness > workplace.get_best_known_fitness():
                ns = Pyro4.locateNS(self.ns_hostname)
                map(lambda w: Pyro4.Proxy(w).set_best_known_fitness(fitness), ns.list(WORKPLACE).values())
        except:
            logging.exception("")
        return workplace.get_best_known_fitness() >= self.minimal_fitness