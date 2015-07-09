from unittest import TestCase
from problem import Task, Job, Problem
from rolling_horizon import JobBacklog


class TestJobBacklog(TestCase):
    def setUp(self):
        self.job_backlog = JobBacklog()
        self.job_2 = Job("jid1", [Task("machine", "duration")], 2)
        self.job_4 = Job("jid1", [Task("machine", "duration")], 4)
        self.job_7 = Job("jid1", [Task("machine", "duration")], 7)

    def test_add_problem(self):
        self.job_backlog.add_problem(Problem([self.job_2, self.job_4, self.job_7]))
        self.assertEqual(self.job_backlog.size(), 3)

    def test_add_job(self):
        self.job_backlog.add_job(self.job_2)
        self.assertEqual(self.job_backlog.size(), 1)

    def test_is_empty_returns_true_when_no_job_was_added(self):
        self.assertTrue(self.job_backlog.is_empty())

    def test_is_empty_returns_false_when_job_was_added(self):
        self.job_backlog.add_job(self.job_2)
        self.assertFalse(self.job_backlog.is_empty())

    def test_is_empty_returns_true_when_all_jobs_are_popped(self):
        self.job_backlog.add_problem(Problem([self.job_2, self.job_4]))
        self.job_backlog.pop_top_priority_job()
        self.job_backlog.pop_top_priority_job()
        self.assertTrue(self.job_backlog.is_empty())

    def test_is_empty_raises_exception_when_popping_from_empty_backlog(self):
        self.assertRaises(Exception, lambda: self.job_backlog.pop_top_priority_job())

    def test_pop_top_priority_job_returns_job_with_earliest_arrival_time(self):
        self.job_backlog.add_problem(Problem([self.job_4, self.job_7, self.job_2]))
        self.assertEqual(self.job_backlog.pop_top_priority_job().arrival_time, 2)
        self.assertEqual(self.job_backlog.pop_top_priority_job().arrival_time, 4)
        self.assertEqual(self.job_backlog.pop_top_priority_job().arrival_time, 7)