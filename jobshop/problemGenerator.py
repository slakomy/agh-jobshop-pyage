from problem import Job, Task, Problem
import copy
import random
from time import time

class Counter(object):
	def __init__(self):
		self.counter = 100
	def get_next(self):
		self.counter += 1
		return self.counter-1

c_obj = Counter()

class Randomized(object):

	def init_random(self, random_obj):
		self._random = random_obj

	def random_check(self):
		if "_random" not in self.__dict__:
			raise Exception("Randomized object not initialized properly")

class Distribution(Randomized):

	def next(self):
		self.random_check()
		return self._next()

	def _next(self):
		raise NotImplementedException()

class UniformIntDistribution(Distribution):

	def __init__(self, start_in, end_in):
		self.start = start_in
		self.end = end_in

	def _next(self):
		return self._random.randint(self.start, self.end)


class ProblemGenerator(object):

	def __init__(self, problemTick, start_problems_provider, incomming_problems_provider):
		self.__problemTick = problemTick
		self.__start_prov = start_problems_provider
		self.__incomm_prov = incomming_problems_provider
		

	def step(self, step_nr):
		if self.check_new_problem(step_nr):
			if step_nr == 1:
				return self.__create_initial_problem()
			else:
				return self.__incomm_prov.generate_problem()


	def check_new_problem(self, step_nr):
		return self.__new_problem_check(step_nr)

	def __new_problem_check(self, step_nr):
		return step_nr % self.__problemTick == 1

	def __create_initial_problem(self):
		return self.__start_prov.generate_problem()

class PredictedProblemGenerator(object):

	def __init__(self, predcited_problems_provider, problems_to_predict_nr):
		self.__pred_prov = predcited_problems_provider
		self.__to_pred_nr = problems_to_predict_nr

	def get_predicted_problems(self):
		return [self.__pred_prov.generate_problem() for _ in xrange(self.__to_pred_nr)]



class RandomizedProblemProvider(object):

	def __init__(self, jobs_number, job_duration_distrib, tasks_number_distrib, tasks_provider, seed=None):
		self.__jobs_nr = jobs_number
		self.__jobs_distrib = job_duration_distrib
		self.__tasks_distrib = tasks_number_distrib
		self.__tasks_provider = tasks_provider
		self.__random = random.Random()
		self.__random.seed(seed)
		self.__init_randoms()

	def __init_randoms(self):
		self.__tasks_provider.init_random(self.__random)
		self.__tasks_distrib.init_random(self.__random)
		self.__jobs_distrib.init_random(self.__random)

	def generate_problem(self):
		return Problem([self.__start_proverate_job() for _ in xrange(self.__jobs_nr)])

	def __start_proverate_job(self):
		job_duration = self.__jobs_distrib.next()
		tasks_number = self.__tasks_distrib.next()
		tasks = self.__tasks_provider.provide(job_duration=job_duration, tasks_number=tasks_number)
		new_job = Job(c_obj.get_next(), tasks)
		return new_job

class RandomizedTasksProvider(object):

	def __init__(self, machines_number):
		self.__machines_nr = machines_number

	def init_random(self, random_obj):
		self.__random = random_obj

	def provide(self, job_duration, tasks_number):
		average = job_duration/tasks_number
		std_dev = average/2
		remaining_duration = job_duration
		tasks = []
		for task_counter in xrange(tasks_number):
			task_machine = self.__random.randint(0,self.__machines_nr-1)
			task_duration = int(self.__random.gauss(average, std_dev))
			positive_task_duration = max(1, task_duration)
			if task_counter == tasks_number-1:
				task_real_duration = remaining_duration
			else:
				task_real_duration = min(remaining_duration, positive_task_duration)
			remaining_duration -= task_real_duration
			tasks.append(Task(task_machine, task_real_duration))
			if remaining_duration ==0:
				break
		return tasks

