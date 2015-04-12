from unittest import TestCase
from mock import MagicMock
from rolling_horizon import JobWindow
from problem import Job, Task


class TestJobWindow(TestCase):
    def setUp(self):
        self.job_window = JobWindow(5)
        task = Task("machine", "duration")
        task.get_duration = MagicMock(return_value=2)
        self.task_2 = task
        task = Task("machine", "duration")
        task.get_duration = MagicMock(return_value=4)
        self.task_4 = task

    def test_add_job_returns_false_when_not_full_after_insertion(self):
        self.assertFalse(self.job_window.add_job(Job("jid", [self.task_2])))

    def test_add_job_returns_true_when_full_after_insertion(self):
        self.assertTrue(self.job_window.add_job(Job("jid", [self.task_2, self.task_4])))

    def test_add_job_raises_exception_when_adding_job_to_full_window(self):
        self.assertTrue(self.job_window.add_job(Job("jid", [self.task_2, self.task_4])))
        self.assertRaises(Exception, lambda: self.job_window.add_job(Job("jid", [self.task_2])))

    def test_is_full_returns_false_when_window_is_empty(self):
        self.assertFalse(self.job_window.is_full())

    def test_is_full_returns_false_when_window_is_not_full(self):
        self.job_window.add_job(Job("jid", [self.task_4]))
        self.assertFalse(self.job_window.is_full())

    def test_is_full_returns_true_when_windows_is_full(self):
        self.job_window.add_job(Job("jid", [self.task_4]))
        self.job_window.add_job(Job("jid", [self.task_2, self.task_4]))
        self.assertTrue(self.job_window.is_full())