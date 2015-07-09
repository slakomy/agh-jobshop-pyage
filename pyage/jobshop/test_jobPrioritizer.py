from unittest import TestCase
from problem import Job, Task
from rolling_horizon import JobPrioritizer


class TestJobPrioritizer(TestCase):
    def test_prioritizes_by_arrival_time(self):
        job = Job("jid", [Task("machine", "duration")], 3)
        self.assertEqual(JobPrioritizer.prioritize(job), 3)