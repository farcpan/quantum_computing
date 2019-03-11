"""
    knapsack.py
"""

import sys
import csv
import time
import dimod
import neal
import numpy as np
from dwave_qbsolv import QBSolv
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
from pyqubo import Array, Constraint, Placeholder, solve_qubo


class KnapsackProblemSolver:
    # qbsolv parameters
    NUM_REPEATS = 100
    VERBOSITY_LEVEL = 0
    ITERATION_MAX = 80
    
    def __init__(self, _cost_list, _value_list, _threshold, ):
        """
            constructor
        """
        self.THRESHOLD = _threshold
        self.COST_LIST = _cost_list
        self.VALUE_LIST = _value_list
    
        _max = 0.0
        for cost in self.COST_LIST:
            if _max < cost:
                _max = cost
        self.LAMBDA = 2.0 * _max

        # QUBO variables
        self.N = len(self.COST_LIST)
        self.q = Array.create('q', shape=self.N, vartype='BINARY')
        self.y = Array.create('y', shape=self.THRESHOLD, vartype='BINARY')


    def calculate(self):
        """
            Calculating
        """
        # model
        hamiltonian0, hamiltonian1 = self._create_hamiltonian(self.q, self.y)
        model = (self.LAMBDA * hamiltonian0 + hamiltonian1).compile()
        qubo, offset = model.to_qubo()

        _sampler = neal.SimulatedAnnealingSampler()
        print("-------------- start calculation --------------")
        #_response = QBSolv().sample_qubo(qubo, num_repeats=NUM_REPEATS, verbosity=VERBOSITY_LEVEL)
        _response = QBSolv().sample_qubo(qubo, num_repeats=self.NUM_REPEATS, verbosity=self.VERBOSITY_LEVEL, solver=_sampler)
        #_response = QBSolv().sample_qubo(qubo, solver=_sampler, solver_limit=49)
        #_response = _sampler.sample_qubo(qubo)
        print("-------------- end calculation --------------")
        return _response


    def analyze(self, _response):
        """
            Analyzing
        """
        #energy_list = _response.data_vectors['energy']
        for r in _response:
            q_tmp = np.array([0 for k in range(len(self.COST_LIST))])
            y_tmp = np.array([0 for k in range(self.THRESHOLD)])

            for k in range(len(self.COST_LIST)):
                q_tmp[k] = r["q[{}]".format(k)]
            for k in range(self.THRESHOLD):
                y_tmp[k] = r["y[{}]".format(k)]

            Energy0, Energy1 = self._create_hamiltonian(q_tmp, y_tmp)
            print("E0={}, E1={}".format(Energy0, Energy1))
            if Energy0 > 0.0:
                return [], [], 0.0
            else:
                return q_tmp, y_tmp, -Energy1


    def _create_hamiltonian(self, _q, _y):
        """
            Calculating Hamiltonian (Energy) of model
        """
        _tmp = 0.0
        for val in _y:
            _tmp += val
        _hamiltonian0 = (1.0 - _tmp)**2

        _tmp_y = 0.0
        _tmp_cost = 0.0
        _tmp_val = 0.0
        for k, val in enumerate(_y):
            _tmp_y += (k+1) * val
        for k, val in enumerate(_q):
            _tmp_cost += self.COST_LIST[k] * val
            _tmp_val -= self.VALUE_LIST[k] * val
        _hamiltonian0 += (_tmp_y - _tmp_cost)**2
        _hamiltonian1 = _tmp_val

        return _hamiltonian0, _hamiltonian1
        


if __name__ == '__main__':
    """
    Input Data
    """
    THRESHOLD   = 15  # Cost threshold (total cost should be equal to or smaller than this value)
    COST_LIST   = [11, 2, 3, 4, 1, 5]
    VALUE_LIST  = [15, 3 ,1, 4, 2, 8]

    # solver instance
    solver = KnapsackProblemSolver(COST_LIST, VALUE_LIST, THRESHOLD)

    maximum = 0.0
    finalCost = 0.0
    finalResult = []
    for index in range(10):
        response = solver.calculate()
        q, y, e = solver.analyze(response)
        if maximum < e:
            maximum = e
            finalResult = q
            for k, val in enumerate(y):
                if val == 1:
                    finalCost = k+1
                    break

    print("max={}, cost={}, q: {}".format(maximum, finalCost, finalResult))
