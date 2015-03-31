class TimeKeeper(object):
	def __init__(self, resolution, init_time):
		self.__time = init_time
		self.__resolution = resolution
		self.__steps = 0

	def step(self):
		self.__steps += 1
		if self.__steps % self.__resolution == 0:
			self.__time += 1

	def get_time(self):
		return self.__time