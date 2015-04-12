class JobWindow(object):
    def __init__(self, predictive_time):
        self.__predictive_time = predictive_time
        self.__total_active_execution_time = 0
        self.__jobs = []

    def add_job(self, job):
        if self.__total_active_execution_time > self.__predictive_time:
            raise Exception("Job window is already full")
        self.__total_active_execution_time += self.__calculate_execution_time(job)
        self.__jobs.append(job)
        return self.is_full()

    def __calculate_execution_time(self, job):
        execution_time = 0
        for task in job.get_tasks_list():
            execution_time += task.get_duration()
        return execution_time

    def is_full(self):
        return self.__total_active_execution_time > self.__predictive_time

    def get_jobs(self):
        return list(self.__jobs)