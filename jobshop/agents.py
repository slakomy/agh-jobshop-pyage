import copy
import logging

from flowshop_genetics import FlowShopEvaluation
from pyage.core.inject import Inject
from problem import TimeMatrixConverter
from problemGenerator import Counter, DistortedProblemGenerator
from rolling_horizon import JobWindow
from rolling_horizon import JobBacklog
from stats import GanttStats

logger = logging.getLogger(__name__)


class MasterAgent(object):
    @Inject("slaves:_MasterAgent__slaves")
    @Inject("manufacture:_MasterAgent__manufacture")
    @Inject("timeKeeper:_MasterAgent__timeKeeper")
    @Inject("stop_condition:_MasterAgent__stop_condition")
    @Inject("problem_provider:_MasterAgent__problem_provider")
    def __init__(self, time_matrix, window_time, distortion_factor=0.1, steps_for_initial_window=100):
        self.__window_time = window_time
        self.__steps_for_initial_window = steps_for_initial_window
        self.__summary_makespan = 0
        self.__windows_calculated = 0
        self.__stop_condition.set_all_jobs_scheduled(False)
        self.__backlog = JobBacklog()
        self.__problem_generator = DistortedProblemGenerator(distortion_factor)
        self.__converter = TimeMatrixConverter(Counter())
        self.__initial_problem = self.__converter.matrix_to_problem(time_matrix)
        self.__tasks_per_job = len(self.__initial_problem.get_jobs_list()[0].get_tasks_list())
        self.__backlog.add_problem(self.__initial_problem)
        self.__history = []
        self.__stats = GanttStats()
        self.__solve_initial_window()
        self.__assign_predicted_windows_to_slaves()


    def __solve_initial_window(self):
        initial_job_window = self.next_job_window()
        logger.info("About to solve initial job window %s", initial_job_window)
        makespan, result_matrix = GeneticsHelper(initial_job_window).solve_with(self.__slaves.values()[0],
                                                                                self.__steps_for_initial_window)
        logger.info("Initial window makespan=%s, result_matrix=%s", str(makespan), str(result_matrix))
        time_matrix = self.__converter.window_to_matrix(initial_job_window)
        for machine_id in xrange(len(result_matrix)):
            for job_id in xrange(len(result_matrix[machine_id])):
                time = time_matrix[machine_id][job_id]
                start_time = result_matrix[machine_id][job_id]
                self.__history.append([machine_id, job_id, start_time, time, 'Tick ' + str(start_time)])
        self.__stats.summarize(self.get_history())
        print self.get_history()

    def next_job_window(self):
        job_window = JobWindow(self.__window_time * (self.__tasks_per_job - 2))
        while not job_window.is_full() and not self.__backlog.is_empty():
            job_window.add_job(self.__backlog.pop_top_priority_job())
        return job_window

    def step(self):
        self.__timeKeeper.step()
        for slave in self.__slaves.values():
            slave.step()
        if self.window_ended():
            self.__accept_new_problem()
            self.__current_window = self.next_job_window()
            logger.info("New job window generated: %s", self.__current_window)
            self.__calculate_schedule_for_current_window()
            if not self.__backlog.is_empty() or self.__problem_provider.has_next():
                self.__assign_predicted_windows_to_slaves()
                self.__timeKeeper.increment()
            else:
                logger.info("No jobs or problems left for next window. Setting stop condition to true")
                self.__stop_condition.set_all_jobs_scheduled(True)
                # print "{0}\t{1}\t{2}\t{3}".format(self.__window_time, len(self.__slaves), self.__windows_calculated,
                #                                   self.__summary_makespan)
                print "{0}\t{1}".format(len(self.__slaves), self.__summary_makespan)


    def window_ended(self):
        return self.__timeKeeper.get_time() % self.__window_time == 0

    def __accept_new_problem(self):
        if self.__problem_provider.has_next():
            incoming_problem = self.__problem_provider.provide_next(self.__timeKeeper.get_time())
            logger.debug("Accepting new problem: %s", incoming_problem)
            logger.info("Incoming problem matrix: %s", str(self.__converter.problem_to_matrix(incoming_problem)))
            self.__backlog.add_problem(incoming_problem)

    def __calculate_schedule_for_current_window(self):
        makespan, result_matrix = GeneticsHelper(self.__current_window).get_best_solution(self.__slaves.values())
        self.__summary_makespan += makespan
        self.__windows_calculated += 1
        logger.info("Job window solution found. Makespan=%s, result_matrix=%s", str(makespan), str(result_matrix))
        # print "makespan=" + str(makespan) + " result_matrix=" + str(result_matrix)
        time_matrix = self.__converter.window_to_matrix(self.__current_window)
        for machine_id in xrange(len(result_matrix)):
            for job_id in xrange(len(result_matrix[machine_id])):
                time = time_matrix[machine_id][job_id]
                start_time = result_matrix[machine_id][job_id]
                self.__history.append([machine_id, job_id, start_time, time, 'Tick ' + str(self.__timeKeeper.get_time() + start_time)])
        self.__stats.summarize(self.get_history())
        print self.get_history()
        # TODO: convert result_matrix to solution and add to manufacture as gantt statistics are generated based on manufacture

    def __assign_predicted_windows_to_slaves(self):
        backlog_jobs = copy.copy(self.__backlog._jobs_priority_queue.queue)
        for slave in self.__slaves.values():
            self.__assign_predicted_window(slave)
            self.__backlog._jobs_priority_queue.queue = backlog_jobs


    def get_history(self):
        return self.__history

    def __assign_predicted_window(self, slave):
        if self.__problem_provider.has_next():
            predicted_problem = self.__problem_generator.generate_distorted_problem(self.__initial_problem,
                                                                                   self.__timeKeeper.get_time() + self.__window_time)
            logger.debug("New predicted problem generated: %s", predicted_problem)
            self.__backlog.add_problem(predicted_problem)
        logger.debug("Generating predicted job window")
        job_window = self.next_job_window()
        logger.debug("Predicted job window generated: %s", job_window)
        time_matrix = self.__converter.window_to_matrix(job_window)
        logger.info("Time matrix for predicted job window: %s", str(time_matrix))
        GeneticsHelper(job_window).reset(slave)


def masters_factory(count, job_window_time, time_matrix, distortion_factor=0.1):
    def factory():
        agents = {}
        for i in xrange(count):
            agent = MasterAgent(time_matrix, job_window_time, distortion_factor)
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


class GeneticsHelper(object):
    def __init__(self, job_window):
        self.time_matrix = TimeMatrixConverter(Counter()).window_to_matrix(job_window)

    def solve_with(self, slave, steps):
        self.reset(slave)
        for _ in xrange(0, steps):
            slave.step()
        return self.get_best_solution([slave])

    def reset(self, slave):
        #TODO: this is based on flowshop_classi_conf, make it more general(operators can have different order)
        slave.operators[2].time_matrix = self.time_matrix  # now slave evaluates schedule accordingly to new job_window
        slave.operators[2].JOBS_COUNT = len(self.time_matrix[0]) + 1
        slave.operators[2].PROCESSORS_COUNT = len(self.time_matrix) + 1
        slave.initializer.permutation_length = len(self.time_matrix[0])
        slave.population = []
        slave.initialize()

    def get_best_solution(self, slaves):
        logger.debug("Searching for best solution for time_matrix %s", self.time_matrix)
        jobs_in_current_window = len(self.time_matrix[0])
        makespans = []
        result_matrices = []
        for slave in slaves:
            permutation = slave.get_best_genotype().permutation
            self.__adjust_permutation(permutation, jobs_in_current_window)
            makespan, result_matrix = FlowShopEvaluation(self.time_matrix).compute_makespan(permutation, True)
            makespans.append(makespan)
            result_matrices.append(result_matrix)
        min_makespan_idx = makespans.index(min(makespans))
        return makespans[min_makespan_idx], result_matrices[min_makespan_idx]

    #Predicted Job Window could have different number of jobs, we have to adjust it
    def __adjust_permutation(self, permutation, jobs_in_current_window):
        while len(permutation) != jobs_in_current_window:
            if len(permutation) > jobs_in_current_window:
                permutation.remove(len(permutation)-1)
            else:
                permutation.append(len(permutation))