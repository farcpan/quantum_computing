'''
knapsack.py
    How to use:
    (1) Activate the `ocean` environment.
    (2) Prepare input file in the `input` directory.
    (3) Start this script by
        $ python numberplace.py [--sample "dwave"]
'''
import sys
import csv
import time
import dimod
import neal
import argparse
from dwave_qbsolv import QBSolv
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite

'''
Input Data
'''
C = 15  # Cost threshold (total cost should be equal to or smaller than this value)
A = 20
B = 1
COST_LIST    = [11, 2, 3, 4, 1, 5]
VALUE_LIST   = [15, 3 ,1, 4, 2, 8]

'''
Parameter adjustment (constant)
'''
QUBO_PARAM_FACTOR = 10.0

'''
Data
'''
qubo = {}               # Qubo variables

'''
Calculation option
'''
NUM_REPEATS = 100
VERBOSITY_LEVEL = 0
ITERATION_MAX = 80

'''
Functions
'''
def get_args():
    _parser = argparse.ArgumentParser()
    _parser.add_argument("--input", help="specify input csv file path.", type=str)
    _parser.add_argument("--sampler", help="specify 'dwave' when using dwave machine.", type=str)
    args = _parser.parse_args()
    return(args)

#
# calculation (tabu search or dwave)
#
def do_calculation(simul):
    if simul == "dwave":
        _sampler = EmbeddingComposite(DWaveSampler())
        _response = QBSolv().sample_qubo(qubo, num_repeats=NUM_REPEATS, verbosity=VERBOSITY_LEVEL, solver=_sampler)
    elif simul == "dimod":
        _sampler = dimod.ExactSolver()
        _response = QBSolv().sample_qubo(qubo, num_repeats=NUM_REPEATS, verbosity=VERBOSITY_LEVEL, solver=_sampler)
    elif simul == "neal":
        _sampler = neal.SimulatedAnnealingSampler()
        _response = QBSolv().sample_qubo(qubo, num_repeats=NUM_REPEATS, verbosity=VERBOSITY_LEVEL, solver=_sampler)
    else:
        _response = QBSolv().sample_qubo(qubo, num_repeats=NUM_REPEATS, verbosity=VERBOSITY_LEVEL);
    return _response

#
# analysis
#
def do_analysis(results):
    _res = []
    _qubo_list = []
    for obj in results:
        _cost = 0
        _value = 0
        _constraint = 0
        _qubo = []
        for res in obj: # each calculation result
            if res < len(VALUE_LIST):
                _qubo.append(obj[res])
                _value += (obj[res] * VALUE_LIST[res])
                _cost += (obj[res] * COST_LIST[res])
            else:
                _constraint += obj[res]

        if _cost <= C and _constraint == 1:
            _qubo_list.append(_qubo)
            _res.append((_value, _cost))
    return _res, _qubo_list
#
# main function
#
def main():
    _simul = "qbsolv"
    _args = get_args()  # command line arguments

    if hasattr(_args, 'sampler'):
        if _args.sampler != None:
            _simul = _args.sampler

    #
    # Parameter Definition
    #
    # h
    _N = len(VALUE_LIST)
    for i in range(_N):
        qubo[(i, i)] = (-B * VALUE_LIST[i] + A * COST_LIST[i] * COST_LIST[i]) / QUBO_PARAM_FACTOR

    for i in range(C):
        qubo[(i + _N, i + _N)] = (A * ((i + 1) * (i + 1) - 1)) / QUBO_PARAM_FACTOR

    # J
    for i in range(C - 1):
        for j in range(i + 1, C):
            if (i + _N, j + _N) in qubo:
                qubo[i + _N, j + _N] += (2 * A * ((i + 1) * (j + 1) + 1)) / QUBO_PARAM_FACTOR
            else:
                qubo[i + _N, j + _N] = (2 * A * ((i + 1) * (j + 1) + 1)) / QUBO_PARAM_FACTOR

    for i in range(_N - 1):
        for j in range(i + 1, _N):
            if (i, j) in qubo:
                qubo[i, j] += (2 * A * COST_LIST[i] * COST_LIST[j]) / QUBO_PARAM_FACTOR
            else:
                qubo[i, j] = (2 * A * COST_LIST[i] * COST_LIST[j]) / QUBO_PARAM_FACTOR

    for i in range(_N):
        for j in range(C):
            if (i, j + _N) in qubo:
                qubo[i, j + _N] += (-2 * A * (j + 1) * COST_LIST[i]) / QUBO_PARAM_FACTOR
            else:
                qubo[i, j + _N] = (-2 * A * (j + 1) * COST_LIST[i]) / QUBO_PARAM_FACTOR

    # calculation
    _start = time.time()

    _tmp = 0
    _tmp_cost = 0
    _tmp_list = []
    for i in range(ITERATION_MAX):
        _response = do_calculation(_simul)
        _result = list(_response.samples())
        _ret, _qubo = do_analysis(_result)

        for k in range(len(_ret)):
            print("{}, {}".format(_ret[k], _qubo[k]))
            if _tmp < _ret[k][0]:
                _tmp = _ret[k][0]
                _tmp_cost = _ret[k][1]
                _tmp_list = _qubo[k]

    _elapsed_time = time.time() - _start
    print("elapsed_time:{} [sec]".format(_elapsed_time))
    print("result: {}, {}, {}".format(_tmp, _tmp_cost, _tmp_list))

#
# execution
#
main()
