import random
from pyage.core.inject import Inject
from pyage.core.operator import Operator
import copy
from pyage.solutions.evolution.mutation import AbstractMutation
from pyage.solutions.evolution.crossover import AbstractCrossover


def swaps_p1_to_p2(p1, p2):
    """
    :type p1: list of int
    :type  p2: list of int
    :rtype: list of (int, int)
    :return: minimal list of swaps necessary to transform p1 into p2
    """

    result = []
    visited = [False] * len(p1)
    position_in_p1 = {p1[i]: i for i in range(len(p1))}

    for i in xrange(len(p1)):
        if not visited[i]:  # start a cycle
            while not visited[i]:
                visited[i] = True
                next_ = position_in_p1[p2[i]]
                result.append((i, next_))
                i = next_
            result.pop()  # last swap is excessive
    return result


def swap(list_, i, j):
    list_[i], list_[j] = list_[j], list_[i]


def rand_bool():
    return random.random() < 0.5


class PermutationGenotype(object):
    def __init__(self, permutation):
        """
        :param permutation: order of processing
                flow shop:
                    a list of consecutive job numbers (0..n-1 NOT 1..n)
                    NOT a list of orders of particular jobs

                    e.g. a permutation (2,0,1) means that job2 is 1st, job0 2nd and job1 3rd
                    NOT job0 is 3rd, job1 1st and job2 2nd
                open shop:
                    See *GAFAPAS* par. Open shop scheduling problem p. 112-113
        :type permutation: list of int
        """
        self.permutation = permutation
        self.fitness = None

    def __str__(self):
        string = "PG[{0}, fitness: {1}]".format(self.permutation, self.fitness)
        return string if self.is_permutation_valid() else "INVALID!: " + string

    def __repr__(self):
        return self.__str__()

    def is_permutation_valid(self):
        def all_ones(occurrences_count):
            return all(map(lambda oc: oc == 1, occurrences_count))

        occurrences_count = [0] * len(self.permutation)
        for item in self.permutation:
            occurrences_count[item] += 1
        return all_ones(occurrences_count)


class PermutationInitializer(Operator):
    def __init__(self, permutation_length, population_size=100):
        super(PermutationInitializer, self).__init__(PermutationGenotype)
        self.permutation_length = permutation_length
        self.population_size = population_size

    def process(self, population):
        for _ in xrange(self.population_size):
            population.append(PermutationGenotype(PermutationInitializer.generate_permutation(self.permutation_length)))

    @staticmethod
    def generate_permutation(permutation_length):
        permutation = range(permutation_length)
        random.shuffle(permutation)
        return permutation


class PermutationMutation(AbstractMutation):
    def __init__(self, random_swaps_count, probability=0.4):
        """:param random_swaps_count: int"""
        super(PermutationMutation, self).__init__(PermutationGenotype, probability)
        self.random_swaps_count = random_swaps_count

    def mutate(self, genotype):
        """:type genotype: PermutationGenotype"""

        def perform_random_swap(permutation):
            """ :param permutation: list of int """
            length = len(permutation)
            i = random.randint(0, length - 1)
            j = random.randint(0, length - 1)
            permutation[i], permutation[j] = permutation[j], permutation[i]

        for _ in xrange(self.random_swaps_count):
            perform_random_swap(genotype.permutation)


class FirstHalfSwapsCrossover(AbstractCrossover):
    def __init__(self, size=100):
        super(FirstHalfSwapsCrossover, self).__init__(PermutationGenotype, size)


    def cross(self, p1, p2):
        """
        :type p1: PermutationGenotype
        :type p2: PermutationGenotype
        :rtype PermutationGenotype
        """

        def perform_first_half_of_swaps(genotype, swaps):
            for (i, j) in FirstHalfSwapsCrossover._first_half(swaps):
                swap(genotype.permutation, i, j)

        swaps = swaps_p1_to_p2(p1.permutation, p2.permutation)
        genotype = PermutationGenotype(list(p1.permutation))
        perform_first_half_of_swaps(genotype, swaps)

        # TODO(vucalur): should return 2 children: from first and second half on the swaps.
        # TODO(vucalur): modify AbstractCrossover so it can handle such usage
        return genotype

    @staticmethod
    def _first_half(list_):
        return list_[:len(list_) // 2]


class MemeticPermutationMutation(PermutationMutation):
    def __init__(self, local_rounds_count, attempts_per_round, random_swaps_count, probability=0.4):
        super(MemeticPermutationMutation, self).__init__(random_swaps_count, probability)
        self.local_rounds_count = local_rounds_count
        self.attempts_per_round = attempts_per_round

    @Inject('evaluation')
    def mutate(self, genotype):
        """:type genotype: PermutationGenotype"""

        def fitness(genotype):
            result = self.evaluation.compute_makespan(genotype.permutation)
            return result

        def do_round():
            def perform_mutation(round_base_genotype):
                candidate_genotype = copy.deepcopy(round_base_genotype)
                super(MemeticPermutationMutation, self).mutate(candidate_genotype)
                candidate_fitness = fitness(candidate_genotype)
                return candidate_fitness, candidate_genotype

            def update_best_if_better(candidate_fitness, candidate_genotype):
                if candidate_fitness < best['fitness']:
                    best['genotype'] = candidate_genotype
                    best['fitness'] = candidate_fitness

            round_base_genotype = copy.deepcopy(best['genotype'])
            for _ in xrange(self.attempts_per_round):
                candidate_fitness, candidate_genotype = perform_mutation(round_base_genotype)
                update_best_if_better(candidate_fitness, candidate_genotype)

        best = {'genotype': genotype, 'fitness': fitness(genotype)}  # why a dict? here: http://stackoverflow.com/a/2609593/1432478
        for _ in xrange(self.local_rounds_count):
            do_round()
        genotype.permutation = best['genotype'].permutation  # genotype = best['genotype'] won't work

class FlowShopEvaluation(Operator):
    def __init__(self, time_matrix):
        super(FlowShopEvaluation, self).__init__(PermutationGenotype)
        self.time_matrix = time_matrix
        self.JOBS_COUNT = len(self.time_matrix[0]) + 1  # + 1: for sentinel column
        self.PROCESSORS_COUNT = len(self.time_matrix) + 1  # + 1: for sentinel row

    def process(self, population):
        """ :type population: list of PermutationGenotype """
        for individual in population:
            individual.fitness = - self.compute_makespan(individual.permutation)

    def compute_makespan(self, permutation, compute_solution_matrix=False):
        """ :return: makespan for processing in order specified by :param permutation: """
        completion_times = self._calculate_completion_times(permutation)
        if compute_solution_matrix:
            return completion_times[-1][-1], completion_times
        else:
            return completion_times[-1][-1]

    def _calculate_completion_times(self, permutation):
        completion_times = self._initialize_including_sentinels()
        for pi in xrange(1, self.PROCESSORS_COUNT):
            for ji in xrange(1, self.JOBS_COUNT):
                completion_times[pi][ji] = self.time_matrix[pi - 1][permutation[ji - 1]] \
                                           + max(completion_times[pi][ji - 1], completion_times[pi - 1][ji])
        completion_times = self._strip_sentinels(completion_times)
        return completion_times

    def _initialize_including_sentinels(self):
        return [[0 for job_i in xrange(self.JOBS_COUNT)]
                for processor_i in xrange(self.PROCESSORS_COUNT)]

    @staticmethod
    def _strip_sentinels(completion_times):
        return [processor[1:] for processor in completion_times[1:]]


class OpenShopEvaluation(Operator):
    def __init__(self, time_matrix):
        super(OpenShopEvaluation, self).__init__(PermutationGenotype)
        self.time_matrix = time_matrix
        self.JOBS_COUNT = len(self.time_matrix[0])
        self.PROCESSORS_COUNT = len(self.time_matrix)

    def process(self, population):
        """ :type population: list of PermutationGenotype """
        for individual in population:
            individual.fitness = - self.compute_makespan(individual.permutation)

    def compute_makespan(self, permutation):
        jobs_cts = self._calculate_jobs_completion_times(permutation)
        return max(jobs_cts)

    def _calculate_jobs_completion_times(self, permutation):
        def update_cts(ct):
            processors_cts[proc_id] = ct
            jobs_cts[job_id] = ct

        # cts - completion_times
        processors_cts = [0 for _ in range(self.PROCESSORS_COUNT)]
        jobs_cts = [0 for _ in range(self.JOBS_COUNT)]
        for permutation_item in permutation:
            job_id, proc_id = self._decode_ids(permutation_item)
            can_start_at = max(processors_cts[proc_id], jobs_cts[job_id])
            task_time = self.time_matrix[proc_id][job_id]
            update_cts(can_start_at + task_time)
        return jobs_cts

    def _decode_ids(self, permutation_item):
        proc_id = permutation_item % self.PROCESSORS_COUNT
        job_id = permutation_item // self.PROCESSORS_COUNT
        return job_id, proc_id
