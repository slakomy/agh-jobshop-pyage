from unittest import TestCase
from problem import Problem, Job, Task, JobUtil
from problemGenerator import DistortedProblemProvider


class TestDistortedProblemProvider(TestCase):
    def setUp(self):
        self.base_problem = Problem([Job("jid1", [Task("machine", 20)]), Job("jid1", [Task("machine", 40)]), Job("jid1", [Task("machine", 70)])])
        self.base_problem_duration = 20 + 40 + 70
        self.distortion_factor = 0.1
        self.distorted_problem_provider = DistortedProblemProvider(self.distortion_factor)

    def test_generated_problem_differs_by_more_than_distortion_factor(self):
        distorted_problem = self.distorted_problem_provider.generate_distorted_problem(self.base_problem)
        diff_time = 0
        distorted_jobs = distorted_problem.get_jobs_list()
        base_jobs = self.base_problem.get_jobs_list()
        for i in xrange(0, len(base_jobs)):
            diff_time += self.__calculate_job_diff_time(base_jobs[i], distorted_jobs[i])
        self.assertGreater(diff_time, self.distortion_factor * self.base_problem_duration )

    def test_base_problem_not_changed_after_providing_distorted_problem(self):
        self.assertEqual(self.base_problem.get_jobs_list()[0].get_tasks_list()[0].duration, 20)
        self.assertEqual(self.base_problem.get_jobs_list()[1].get_tasks_list()[0].duration, 40)
        self.assertEqual(self.base_problem.get_jobs_list()[2].get_tasks_list()[0].duration, 70)

    def __calculate_job_diff_time(self, base_job, distorted_job):
        diff_time = 0
        base_task_list = base_job.get_tasks_list()
        distorted_task_list = distorted_job.get_tasks_list()
        for i in xrange(0, len(base_task_list)):
            diff_time += abs(base_task_list[i].get_duration() - distorted_task_list[i].get_duration())
        return diff_time