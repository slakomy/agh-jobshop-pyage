from os import sep
from os import path
from os import makedirs
import matplotlib.pyplot as plt

class GanttGenerator(object):
    __tasks = {}
    __N = 50
    __n_machines = 0
    __fig = plt.figure(figsize=(16,8))

    __colors = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

    def __init__(self, out_dir='gantt'):
        self.__out_dir = out_dir
        if not path.exists(out_dir):
            makedirs(out_dir)
        for i in range(len(self.__colors)):
            r, g, b = self.__colors[i]
            self.__colors[i] = (r / 255., g / 255., b / 255.)

    def add_task(self, machine_nr, job_nr, start_time, duration):
        if machine_nr not in self.__tasks.keys():
            self.__tasks[machine_nr] = {}
            self.__n_machines = self.__n_machines + 1

        machine = self.__tasks[machine_nr]
        machine[start_time] = {'job_nr': job_nr, 'duration': duration}

    def generate(self, title=None):
        max_duration = 0
        for machine_nr in self.__tasks:
            machine = self.__tasks[machine_nr]
            for start_time in machine:
                job_nr = machine[start_time]['job_nr']
                duration = machine[start_time]['duration']
                color = self.__colors[job_nr % len(self.__colors)]

                plt.hlines(machine_nr, start_time, start_time + duration, colors=color, lw=50)
                plt.text(start_time + 0.1, machine_nr + 0.1, str(job_nr), bbox=dict(facecolor='white', alpha=1.0)) #fontdict=dict(color='white'))

                if duration + start_time > max_duration:
                    max_duration = duration + start_time

        plt.margins(1)
        if self.__n_machines is 0:
            plt.axis([0, max_duration, 0.8, len(self.__tasks)])
        else:
            plt.axis([0, max_duration, -0.8, self.__n_machines])
        plt.xticks(range(0, max_duration, 1))
        if title:
            plt.title(title)
        plt.xlabel("Time")
        plt.ylabel("Machines")
        if self.__n_machines is 0:
            plt.yticks(range(0, len(self.__tasks), 1))
        else:
            plt.yticks(range(0, self.__n_machines, 1))

        self.__fig.savefig(self.__out_dir + sep + title + '.png')
