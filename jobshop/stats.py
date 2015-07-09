from gantt_generator import GanttGenerator

class GanttStats():

    def __init__(self):
        self.gantt = GanttGenerator('gantt')

    def update(self, step_count, agents):
        pass

    def summarize(self, stats):
        for a in stats:
            self.gantt.add_task(a[0], a[1], a[2], a[3])
            self.gantt.generate(a[4])