import copy
from pyage.core.operator import Operator
import logging

logger = logging.getLogger(__name__)


class Problem(object):
    def __init__(self, jobs_list):
        self.jobs_list = jobs_list

    def __str__(self):
        return "Problem consisted of: \n" + "\n".join(map(str, self.jobs_list))

    def get_jobs_list(self):
        return list(copy.deepcopy(self.jobs_list))

    def get_job_by_jid(self, jid):
        for job in self.jobs_list:
            if job.jid == jid:
                return job

    def merge_with(self, prob):
        new_jobs_list = self.get_jobs_list() + prob.get_jobs_list()
        return Problem(new_jobs_list)

    def __eq__(self, other):
        return self.jobs_list == other.jobs_list

    def represents_same(self, other):
        for job in self.get_jobs_list():
            for other_job in other.get_jobs_list():
                if other_job.represents_same(job):
                    break
                return False
        return True

    def represents_superProblem(self, subOther):
        for job in self.get_jobs_list():
            for subjob in subOther.get_jobs_list():
                if job.represents_superjob(subjob):
                    break
                return False
        return True


class Job(object):
    def __init__(self, jid, tasks_list):
        self.jid = jid
        self.tasks_list = tasks_list
        for task in tasks_list:
            task.job = self

    def __str__(self):
        caption = self.str_of_job_name()
        joined = "\n\t".join(map(lambda x: x.get_str_without_jobnr(), self.tasks_list))
        return caption + "\n\t" + joined

    def setJid(self,jid):
        self.jid = jid

    def str_of_job_name(self):
        return "Job " + str(self.jid)

    def __repr__(self):
        return self.__str__()

    def get_tasks_list(self):
        return self.tasks_list

    def get_jid(self):
        return self.jid

    def get_task_for_machine(self, mid):
        for task in self.tasks_list:
            if task.get_task_machine() is mid:
                return task
        raise Exception()

    def __eq__(self, other):
        # return self.tasks_list == other.tasks_list
        return self.jid == other.jid

    def represents_same(self, other):
        return self.tasks_list == other.tasks_list

    def represents_superjob(self, potentialSubjob):
        for i in xrange(0, len(potentialSubjob.tasks_list)):
            subtask = potentialSubjob.tasks_list[i]
            try:
                task = self.tasks_list[i]
            except IndexError:
                print "Index error"
                return False
            print i
            print subtask
            print task
            if (task.get_task_machine() == subtask.get_task_machine()
                and task.get_duration() >= subtask.get_duration()):
                print "same joooob"
            else:
                return False
        return True


class Task(object):
    def __init__(self, machine, duration):
        self.machine = machine
        self.duration = duration
        self.start_time = -1

    def __str__(self):
        return "Start at " + str(self.start_time) + " Task of job: " + str(self.job.jid) + " at machine: " + str(
            self.machine) + " lasting: " + str(self.duration)

    def get_str_without_jobnr(self):
        return "Task at machine: " + str(self.machine) + " lasting: " + str(self.duration)


    def get_duration(self):
        return self.duration

    def set_start_time(self, time):
        self.start_time = time

    def get_start_time(self):
        return self.start_time

    def get_task_machine(self):
        return self.machine

    def get_task_job(self):
        return self.job

    def __eq__(self, other):
        return self.machine == other.machine and self.duration == other.duration


class Solution(object):
    def __init__(self, machines_nr):
        self.__machines_nr = machines_nr
        self.__machines_start_times = {}
        self.__machines_end_times = {}
        self.__machines_tasks = {}
        self.__initialize_machines_dicts(machines_nr)

    def __initialize_machines_dicts(self, machines_nr):
        for i in xrange(machines_nr):
            self.__machines_start_times[i] = []
            self.__machines_tasks[i] = []
            self.__machines_end_times[i] = 0

    def append_task_to_machine(self, task, timestamp=0):
        machine_nr = task.get_task_machine()
        self.__machines_tasks[machine_nr].append(task)
        self.__machines_end_times[machine_nr] = task.get_start_time() + task.get_duration()

    def get_completion_time(self):
        return max(self.__machines_end_times.values())

    def pop_head_task(self, machine_number, time):
        head_task = self.__machines_tasks[machine_number][0]
        print "TASK IN QUESTION: " + str(head_task)
        if time < head_task.get_start_time():
            raise IndexError
        print "PASSED"
        self.__remove_first_task(machine_number)
        return head_task

    def get_tasks(self, machine_number):
        return self.__machines_tasks[machine_number]

    def remove_last_task(self, machine_number):
        self.__machines_tasks[machine_number] = self.__machines_tasks[machine_number][:-1]

    def __remove_first_task(self, machine_number):
        self.__machines_tasks[machine_number].remove(self.__machines_tasks[machine_number][0])

    def append_clone_more_solution_part(self, new_solution):
        raw_tasks = []
        for m_nr in xrange(self.__machines_nr):
            old_tasks = self.get_tasks(m_nr)
            new_tasks = new_solution.get_tasks(m_nr)
            raw_tasks.append(copy.deepcopy(old_tasks + new_tasks))
        new_solution = Solution(self.__machines_nr)
        for m_nr in xrange(self.__machines_nr):
            for task in raw_tasks[m_nr]:
                new_solution.append_task_to_machine(task)

        return new_solution


    def adjustTasksWithTime(self, time):
        for machine in self.__machines_tasks:
            for task in self.__machines_tasks[machine]:
                task.set_start_time(task.get_start_time() + time)

    def adjustSolutionToSubProblem(self, problem, oldPredictedProblem):
        for machine in self.__machines_tasks:
            for task in self.__machines_tasks[machine]:
                for oldJob in oldPredictedProblem.jobs_list:
                    if task.get_task_job().represents_same(oldJob):

                        print 'they represent same!!'
                        print task.get_task_job()
                        print oldJob
                        returnTask = self.get_equivalent_task_from_problem(task, problem)
                        if returnTask.duration == 0:
                            self.__machines_tasks[machine].remove(task)
                        else:
                            task.duration = self.get_equivalent_task_from_problem(task, problem).duration



    def get_equivalent_task_from_problem(self, task, problem):
        print "insider:"
        print problem
        joblist = problem.get_jobs_list()
        flag = False
        if len(joblist) == 1:
            for taskk in joblist[0].tasks_list:
                if taskk.machine == task.machine:
                    wantedTask = taskk
                    flag = True
                    break
                else:
                    print "taskk: " + str(taskk)
                    print "task: " + str(task)
            if not flag:
                return Task(0, 0)
            print task.duration
            print wantedTask.duration
            if (task.duration < wantedTask.duration):
                print "something is fucked up"
            joblist[0].tasks_list.remove(wantedTask)
            return wantedTask
        else:
            same_machine_tasks = []
            for job in joblist:
                for new_task in job.task_list:
                    if new_task.machine == task.machine:
                        same_machine_tasks.append(new_task)

            same_machine_tasks.sort(key=lambda t: t.duration)
            return same_machine_tasks[0]


    def __str__(self):
        machine_strings_list = []
        for m_nr in xrange(self.__machines_nr):
            machine_string = "MACHINE " + str(m_nr) + ":"
            jobs_string = "\n\t".join(map(str, self.__machines_tasks[m_nr]))
            jobs_string = "\n\t" + jobs_string
            machine_strings_list.append(machine_string + jobs_string)
        machine_strings_list = ["Completion time: " + str(self.get_completion_time())] + machine_strings_list
        return "\n".join(machine_strings_list)
