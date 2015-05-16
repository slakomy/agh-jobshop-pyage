from pyage.jobshop.flowshop_genetics import FlowShopEvaluation
import copy
from pyage.core.inject import Inject
import logging
from pyage.jobshop.problem import TimeMatrixConverter
from pyage.jobshop.problemGenerator import Counter, DistortedProblemProvider
from pyage.jobshop.rolling_horizon import JobWindow
from rolling_horizon import JobBacklog

logger = logging.getLogger(__name__)


class MasterAgent(object):
    @Inject("slaves:_MasterAgent__slaves")
    @Inject("manufacture:_MasterAgent__manufacture")
    @Inject("timeKeeper:_MasterAgent__timeKeeper")
    def __init__(self, time_matrix, window_time, steps_for_initial_window=100):
        self.__current_time_matrix = time_matrix
        self.__window_time = window_time
        self.__steps_for_initial_window = steps_for_initial_window
        self.__backlog = JobBacklog()
        self.__problem_provider = DistortedProblemProvider()
        self.__converter = TimeMatrixConverter(Counter())
        self.__initial_problem = self.__converter.matrix_to_problem(time_matrix)
        self.__solve_initial_problem()
        self.__open_new_window()

    def __solve_initial_problem(self):
        logger.debug("Initial problem %s", str(self.__initial_problem))
        self.__backlog.add_problem(self.__initial_problem)
        initial_job_window = self.next_job_window()
        logger.debug("About to solve initial job window %s", initial_job_window)
        self.__solve(self.__converter.window_to_matrix(initial_job_window))

    def next_job_window(self):
        job_window = JobWindow(self.__window_time)
        while not job_window.is_full() and not self.__backlog.is_empty():
            job_window.add_job(self.__backlog.pop_top_priority_job())
        return job_window

    def __solve(self, time_matrix):
        #TODO: this is based on flowshop_classi_conf, make it more general(operators can have different order)
        for slave in self.__slaves.values():
            slave.operators[2].time_matrix = time_matrix
            slave.operators[2].JOBS_COUNT = len(time_matrix[0]) + 1
            slave.operators[2].PROCESSORS_COUNT = len(time_matrix) + 1

        logger.debug("About to solve time_matrix=%s", str(time_matrix))
        slave = self.__slaves.values()[0]
        for _ in xrange(0, 100):
            slave.step()
        permutation = slave.get_best_genotype().permutation
        makespan, result_matrix = result_matrix = FlowShopEvaluation(time_matrix).compute_makespan(permutation, True)
        logger.debug("Solution for initial job window found. Makespan=%s, result_matrix=%s", str(makespan), str(result_matrix))
        #TODO: convert matrix to solution and add to manufacture as gantt statistics are generated based on manufacture

    def step(self):
        self.__timeKeeper.step()
        for slave in self.__slaves.values():
            slave.step()
        if self.window_ended():
            self.__accept_new_problem()
            self.__close_current_window()
            self.__open_new_window()
            #remember to add to each time in matrix current time from timeKeeper, because solution is made assuming that each window starts on time=0
            self.__timeKeeper.increment() #temporary workaround because one time unit consists of more than one step and we would open new window several times in a row

    def window_ended(self):
        return self.__timeKeeper.get_time() % self.__window_time == 0

    def __accept_new_problem(self):
        incoming_problem = self.__problem_provider.generate_distorted_problem(self.__initial_problem)
        logger.debug("Accepting new problem: %s", incoming_problem)
        self.__backlog.add_problem(incoming_problem)
        job_window = self.next_job_window()
        logger.debug("New job window generated: %s", job_window)
        time_matrix = self.__converter.window_to_matrix(job_window)
        self.__current_time_matrix = time_matrix

    def __close_current_window(self):
        makespan, result_matrix = self.get_best_solution()
        logger.debug("Job window solution found. Makespan=%s, result_matrix=%s", str(makespan), str(result_matrix))
        # TODO: convert result_matrix to solution and add to manufacture as gantt statistics are generated based on manufacture

    def get_best_solution(self):
        best_makespan = None
        best_result_matrix = None
        logger.debug("Searching for best solution for time_matrix %s", self.__current_time_matrix)
        for slave in self.__slaves.values():
            permutation = slave.get_best_genotype().permutation
            makespan, result_matrix = FlowShopEvaluation(self.__current_time_matrix).compute_makespan(permutation, True)
            logger.debug("Checking solution with makespan=%s", makespan)
            if best_makespan is None or best_makespan > makespan:
                logger.debug("Makespan better than recently found best solution.")
                best_makespan = makespan
                best_result_matrix = result_matrix
        return best_makespan, best_result_matrix

    def __open_new_window(self):
        logger.debug("Opening new window")
        backlog_jobs = copy.copy(self.__backlog._jobs_priority_queue.queue)
        for slave in self.__slaves.values():
            self.__assign_predicted_problem(slave)
            self.__backlog._jobs_priority_queue.queue = backlog_jobs

    def reset_slave(self, slave, jobs_in_window, time_matrix):
        #TODO: this is based on flowshop_classi_conf, make it more general(operators can have different order)
        slave.operators[2].time_matrix = time_matrix  # now slave evaluates schedule accordingly to new job_window
        slave.initializer.permutation_length = jobs_in_window
        slave.population = []
        slave.initialize()

    def get_history(self):
        return self.__manufacture.get_history()

    def __assign_predicted_problem(self, slave):
        predicted_problem = self.__problem_provider.generate_distorted_problem(self.__initial_problem)
        logger.debug("New predicted problem generated: %s", predicted_problem)
        self.__backlog.add_problem(predicted_problem)
        logger.debug("Generating predicted job window")
        job_window = self.next_job_window()
        logger.debug("Predicted job window generated: %s", job_window)
        time_matrix = self.__converter.window_to_matrix(job_window)
        # self.__current_time_matrix = time_matrix
        logger.debug("Time matrix for predicted job window: %s", str(time_matrix))
        self.reset_slave(slave, len(job_window.get_jobs()), time_matrix)


def masters_factory(count, job_window_time, time_matrix):
    def factory():
        agents = {}
        for i in xrange(count):
            agent = MasterAgent(time_matrix, job_window_time)
            agents["Master_" + str(i)] = agent
        return agents
    return factory


def slaves_factory(count):
    return _agents_factory(count, SlaveAgent)


def _agents_factory(count, agent_type):
    def factory():
        agents = {}
        for i in xrange(count):
            agent = agent_type(i)
            agents["Master_" + str(i)] = agent
        return agents
    return factory
