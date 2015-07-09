import logging
from pyage.core.statistics import Statistics
from gantt_generator import GanttGenerator

logger = logging.getLogger(__name__)

class DummyStats(Statistics):

	def __init__(self, step_res):
		self.step_res = step_res

	def update(self, step_count, agents):
		if step_count % self.step_res == 0:
			best_agent = min(agents, key= lambda x: x.get_fitness)
			logger.info("\nBEST SOLUTION:\n%s",
				best_agent.get_solution())

	def summarize(self, agents):
		pass

class GanttStatistics():
    gantt = GanttGenerator('gantt')
    def update(self, step_count, agents):
        pass

    def summarize(self, stats):
        for a in stats:
            self.gantt.add_task(a[0], a[1], a[2], a[3])
            self.gantt.generate(a[4])
