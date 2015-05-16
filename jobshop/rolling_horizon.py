from Queue import PriorityQueue
from problem import JobUtil


class JobWindow(object):
    def __init__(self, predictive_time):
        self.__predictive_time = predictive_time
        self.__total_active_execution_time = 0
        self.__jobs = []

    def add_job(self, job):
        if self.__total_active_execution_time > self.__predictive_time:
            raise Exception("Job window is already full")
        self.__total_active_execution_time += JobUtil.calculate_active_execution_time(job)
        self.__jobs.append(job)
        return self.is_full()

    def is_full(self):
        return self.__total_active_execution_time > self.__predictive_time

    def get_jobs(self):
        return list(self.__jobs)

    def __str__(self):
        return "JobWindow [predictive_time=" + str(self.__predictive_time) + ", total_active_execution_time=" + \
               str(self.__total_active_execution_time) + ", jobs=" + str(self.__jobs) + "]"


class JobBacklog(object):
    def __init__(self):
        self._jobs_priority_queue = PriorityQueue()

    def add_problem(self, problem):
        for job in problem.jobs_list:
            self.add_job(job)

    def add_job(self, job):
        self._jobs_priority_queue.put((JobPrioritizer.prioritize(job), job))

    def is_empty(self):
        return self._jobs_priority_queue.empty()

    def pop_top_priority_job(self):
        if self.is_empty():
            raise Exception("Backlog is empty")
        return self._jobs_priority_queue.get()[1]

    def size(self):
        return self._jobs_priority_queue.qsize()


class JobPrioritizer(object):
    @staticmethod
    def prioritize(job):
        return job.arrival_time