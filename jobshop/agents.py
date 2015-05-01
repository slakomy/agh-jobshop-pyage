from pyage.jobshop.flowshop_genetics import FlowShopEvaluation
from pyage.jobshop.genetic_classes import *
from pyage.core.inject import Inject
import logging
from pyage.jobshop.problem import TimeMatrixConverter
from pyage.jobshop.problemGenerator import Counter, DistortedProblemProvider
from pyage.jobshop.rolling_horizon import JobWindow
from rolling_horizon import JobBacklog

logger = logging.getLogger(__name__)


# class MasterAgent(object):
#     @Inject("slaves:_MasterAgent__slaves")
#     @Inject("problemGenerator:_MasterAgent__problemGenerator")
#     @Inject("predictedProblemGenerator:_MasterAgent__predictor")
#     @Inject("timeKeeper:_MasterAgent__timeKeeper")
#     @Inject("manufacture:_MasterAgent__manufacture")
#     def __init__(self, name=None):
#         self.name = name
#         super(MasterAgent, self).__init__()
#         for agent in self.__slaves.values():
#             agent.parent = self
#         logger.debug("Slaves number: %d", len(self.__slaves.values()))
#         self.__backlog = JobBacklog()
#         self.steps = 1
#
#     def get_history(self):
#         return self.__manufacture.get_history()
#
#     def step(self):
#         self.__timeKeeper.step()
#         if (not self.__manufacture.tasks_assigned()) and (self.__timeKeeper.get_time() == 0):
#             self.__manufacture.assign_tasks(self.get_solution(self.__timeKeeper.get_time()))
#             self.__assign_predicted_and_solution_part()
#         self.__manufacture.time_tick(self.__timeKeeper.get_time())
#         if self._MasterAgent__problemGenerator.check_new_problem(self.steps):
#             new_problem = self.__problemGenerator.step(self.steps)
#             logger.debug("New problem came: \n%s", new_problem)
#             failed_count = 0
#             for agent in self.__slaves.values():
#                 if(self.steps == 1):
#                     agent.append_problem(new_problem, None)
#                 else:
#                     if agent.check_predicated_problem(new_problem):
#                         logger.debug("Agent with good pred_problem")
#                         print "we're good"
#                         new_solution = agent.get_solution()
#                         print new_solution
#                         new_solution.adjustTasksWithTime(self.__timeKeeper.get_time())
#                         print "adjusted"
#                         print new_solution
#                         print self.__timeKeeper.get_time()
#                         #logger.debug("Pretty new solution\n %s",new_solution)
#                         self.__manufacture.assign_tasks(new_solution)
#                         self.__assign_predicted_and_solution_part()
#                         break
#                     else:
#                         failed_count += 1
#             if failed_count == len(self.__slaves.values()):
#                 print "WHOOOPS"
#                 print new_problem
#                 flag = False
#                 for agent in self.__slaves.values():
#                     if agent.is_prediction_acceptable(new_problem):
#                         print agent.predicted_problem
#                         print "ADJUSTING!!!!"
#                         print new_problem
#                         new_solution = agent.get_solution()
#                         new_solution.adjustSolutionToSubProblem(new_problem,agent.predicted_problem)
#                         new_solution.adjustTasksWithTime(self.__timeKeeper.get_time())
#                         #logger.debug("Pretty new solution\n %s",new_solution)
#                         self.__manufacture.assign_tasks(new_solution)
#                         self.__assign_predicted_and_solution_part()
#                         flag = True
#                         break
#                 if not flag:
#                     print "no prediction worked, assign however"
#                     solution = BasicJobShopEvaluation(self.__manufacture.machines_nr).schedule(JobShopGenotype(new_problem).genes)
#                     solution.adjustTasksWithTime(self.__timeKeeper.get_time()+1) #+1 due to starting -1?
#                     print "lets see"
#                     print new_problem
#                     print solution
#                     self.__manufacture.assign_tasks(solution)
#                     self.__assign_predicted_and_solution_part()
#         for agent in self.__slaves.values():
#             agent.step()
#         self.steps += 1
#
#     def __get_predicted_and_solution_problems(self, solution_part_problem):
#         predicted = self.__predictor.get_predicted_problems()
#         merged_problems  = {}
#         for pred in predicted:
#             merged_problems[solution_part_problem.merge_with(pred)]=pred
#         return merged_problems
#
#     def __assign_predicted_and_solution_part(self):
#         solution_part_problem = self.__manufacture.get_solution_part_as_problem(2)
#         merged_problems = self.__get_predicted_and_solution_problems(solution_part_problem)
#         if len(self.__slaves) != len(merged_problems):
#             raise Exception("Not equal: agents and predicted problems")
#         for it in xrange(len(self.__slaves)):
#             merged_problem = merged_problems.keys()[it]
#             self.__slaves.values()[it].append_problem(merged_problem, merged_problems[merged_problem])
#     def get_agents(self):
#         return self.__slaves.values()
#
#     def get_fitness(self):
#         min_fitness_agent = min(self.__slaves.values(), key=lambda x: x.get_fitness)
#         logger.debug("Taken fitness is %d\n", min_fitness_agent.get_fitness())
#         return min_fitness_agent.get_fitness()
#
#     def get_solution(self, time):
#         min_fitness_agent = min(self.__slaves.values(), key=lambda x: x.get_fitness)
#         solution = min_fitness_agent.get_solution()
#         solution.adjustTasksWithTime(time)
#         return solution

# class SlaveAgent(object):
#     @Inject("mutation:_SlaveAgent__mutation")
#     @Inject("evaluation:_SlaveAgent__evaluation")
#     @Inject("selection:_SlaveAgent__selection")
#     def __init__(self, aid):
#         self.steps = 1
#         self.aid = aid
#         self.fitness = None
#         self.population = []
#
#     def append_problem(self, problem, predicted_problem):
#         #logger.debug("%d New problem for slave appended: \n%s\n with predicted\n %s ", self.aid, problem, predicted_problem)
#         self.population = [JobShopGenotype(problem)]
#         self.predicted_problem = predicted_problem
#         #print "append problem thingy"
#         #print self.__evaluation.schedule(self.population[0].genes)
#
#     def step(self):
#         #logger.debug("Slave step")
#         self.population.append(self.__mutation.mutate(self.population))
#         self.__evaluation.process(self.population)
#         self.__selection.process(self.population)
#         self.fitness = self.population[0].fitness
#         self.steps += 1
#
#     def get_fitness(self):
#         if self.fitness is None:
#
#             self.__evaluation.process(self.population)
#             self.fitness = self.population[0].fitness
#         return self.fitness
#
#     def get_solution(self):
#         print "get solution"
#         print self.__evaluation.schedule(self.population[0].genes)
#         return self.__evaluation.schedule(self.population[0].genes)
#
#     def check_predicated_problem(self, checked_problem):
#         if checked_problem.represents_same(self.predicted_problem):
#             logger.debug("%d Checked: %s\n",self.aid, checked_problem)
#             logger.debug("%d predicted: %s\n",self.aid, self.predicted_problem)
#             return True
#
#     def is_prediction_acceptable(self,problem_that_came):
#         if self.predicted_problem.represents_superProblem(problem_that_came):
#             print "prediction acceptable, cool"
#             return True


class MasterAgent(object):
    @Inject("slaves:_MasterAgent__slaves")
    @Inject("manufacture:_MasterAgent__manufacture")
    @Inject("timeKeeper:_MasterAgent__timeKeeper")
    def __init__(self, time_matrix, window_time):
        self.__current_time_matrix = time_matrix
        self.__window_time = window_time
        self.__backlog = JobBacklog()
        self.__problem_provider = DistortedProblemProvider()
        self.__converter = TimeMatrixConverter(Counter())
        self.__initial_problem = self.__converter.matrix_to_problem(time_matrix)
        logger.debug("Initial problem=%s", str(self.__initial_problem))
        self.__backlog.add_problem(self.__initial_problem)
        initial_job_window = self.next_job_window()
        logger.debug("Initial job window=%s", initial_job_window)
        self.__solve(self.__converter.window_to_matrix(initial_job_window))
        self.__open_new_window()

    def next_job_window(self):
        job_window = JobWindow(self.__window_time)
        while not job_window.is_full() and not self.__backlog.is_empty():
            job_window.add_job(self.__backlog.pop_top_priority_job())
        return job_window

    def __solve(self, time_matrix):
        logger.debug("About to solve time_matrix=%s", str(time_matrix))
        slave = self.__slaves.values()[0]
        #TODO: this is based on flowshop_classi_conf, make it more general(operators can have different order)
        slave.operators[2].time_matrix = time_matrix
        slave.operators[2].JOBS_COUNT = len(time_matrix[0]) + 1
        slave.operators[2].PROCESSORS_COUNT = len(time_matrix) + 1

        for _ in xrange(0, 100):
            slave.step()
        permutation = slave.get_best_genotype().permutation
        makespan, result_matrix = result_matrix = FlowShopEvaluation(time_matrix).compute_makespan(permutation, True)
        logger.debug("Solution for initial job window found. Makespan=%s, result_matrix=%s", str(makespan), str(result_matrix))
        #TODO: convert matrix to solution and add to manufacture as gantt statistics are generated based on manufacture

    #assuming we have only one slave
    def step(self):
        slave = self.__slaves.values()[0]
        self.__timeKeeper.step()
        slave.step()
        if self.__timeKeeper.get_time() % self.__window_time == 0:
            permutation = slave.get_best_genotype().permutation
            makespan, result_matrix = result_matrix = FlowShopEvaluation(self.__current_time_matrix).compute_makespan(permutation, True)
            logger.debug("Job window solution found. Makespan=%s, result_matrix=%s", str(makespan), str(result_matrix))
            #TODO: convert result_matrix to solution and add to manufacture as gantt statistics are generated based on manufacture

            logger.debug("Opening new window")
            self.__open_new_window()
            #remember to add to each time in matrix current time from timeKeeper, because solution is made assuming that each window starts on time=0
            self.__timeKeeper.increment() #temporary workaround because one time unit consists of more than one step and we would open new window several times in a row

    def __open_new_window(self):
        new_problem = self.__problem_provider.generate_distorted_problem(self.__initial_problem)
        logger.debug("New problem generated: %s", new_problem)
        self.__backlog.add_problem(new_problem)
        logger.debug("Generating new job window")
        job_window = self.next_job_window()
        logger.debug("New job window generated: %s", job_window)
        time_matrix = self.__converter.window_to_matrix(job_window)
        self.__current_time_matrix = time_matrix
        logger.debug("Time matrix for new job window: ", str(time_matrix))
        self.reset_slaves(job_window, time_matrix)

    def reset_slaves(self, job_window, time_matrix):
        #TODO: this is based on flowshop_classi_conf, make it more general(operators can have different order)
        self.__slaves.values()[0].operators[2].time_matrix = time_matrix  # now slave evaluates schedule accordingly to new job_window
        self.__slaves.values()[0].initializer.permutation_length = len(job_window.get_jobs())
        self.__slaves.values()[0].population = []
        self.__slaves.values()[0].initialize()

    def get_history(self):
        return self.__manufacture.get_history()


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
