import logging
from pyage.core.statistics import Statistics
from pyage.jobshop.gantt_generator import GanttGenerator

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

class GanttStatistics(Statistics):
    gantt = GanttGenerator('gantt')
    def update(self, step_count, agents):
        pass

    def summarize(self, agents):
        i = 1
        for a in agents:
            for his in a.get_history():
                self.gantt.add_task(his[0], his[1], his[2], his[3])
                self.gantt.generate('Agent ' + str(i) + '-' + his[4])
