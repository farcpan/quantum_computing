'''
numberplace.py
    How to use:
    (1) Activate the `ocean` environment.
    (2) Prepare input file in the `input` directory.
    (3) Start this script by
        $ python numberplace.py [--input "input file path"] [--sample "dwave"]
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
Parameter adjustment (constant)
    Param = (-1.0 - QUBO_PARAM_DELTA) / QUBO_PARAM_FACTOR
'''
QUBO_PARAM_DELTA = 4.0
QUBO_PARAM_FACTOR = 10.0

'''
Data
'''
qubo = {}               # Qubo variables
number_place_in  = []   # Numberplace input data
number_place_out = []   # Numberplace output data

'''
Input Data Size
'''
SUBMATRIX_SIZE = 3
MATRIX_SIZE = SUBMATRIX_SIZE * SUBMATRIX_SIZE

'''
Calculation option
'''
NUM_REPEATS = 50
VERBOSITY_LEVEL = 0
ITERATION_MAX = 10

'''
Functions
'''
def get_args():
    _parser = argparse.ArgumentParser()
    _parser.add_argument("--input", help="specify input csv file path.", type=str)
    _parser.add_argument("--sampler", help="specify 'dwave' when using dwave machine.", type=str)
    args = _parser.parse_args()
    return(args)

# qubo index
def get_index(i, j, k):
    # i -> y: 0 - 8
    # j -> x: 0 - 8
    # k -> num: 0 - 8 (not 1 - 9)
    return i * MATRIX_SIZE * MATRIX_SIZE + j * MATRIX_SIZE + k

#
# area:  0 1 2
#        3 4 5
#        6 7 8
# index: 0 1 2
#        3 4 5
#        6 7 8
# num: 0 - 8 (not 1 - 9)
#
def convert_area_to_index(area, index, num):
    _tmp_i = ((area // SUBMATRIX_SIZE) * SUBMATRIX_SIZE) + (index // SUBMATRIX_SIZE)
    _tmp_j = ((area % SUBMATRIX_SIZE) * SUBMATRIX_SIZE) + (index % SUBMATRIX_SIZE)
    return get_index(_tmp_i, _tmp_j, num)

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
    _i = 0
    _counts = 0
    for obj in results:
        _value = 0
        for res in obj: # each calculation result
            _counts += 1
            _value += (obj[res] * _counts)
            if _counts == MATRIX_SIZE:
                number_place_out.append(_value)
                _counts = 0
                _value = 0
        _i += 1

        # Match Check
        _match = 0
        for kk in range(len(number_place_in)):
            if (number_place_in[kk] > 0) and (number_place_in[kk] != number_place_out[kk]):
                _match += 1

        # Rule Check
        _invalid = 0
        # value check
        for kk in range(MATRIX_SIZE * MATRIX_SIZE):
            if (number_place_out[kk] <= 0) or (number_place_out[kk] > MATRIX_SIZE):
                _invalid += 1
        # J
        for i in range(MATRIX_SIZE):
            for j in range(MATRIX_SIZE):
                for k1 in range(MATRIX_SIZE - 1):
                    for k2 in range(k1 + 1, MATRIX_SIZE):
                        _val1 = get_index(i, j, k1)
                        _val2 = get_index(i, j, k2)
                        _invalid += obj[_val1] * obj[_val2]

        # row & colomn
        for i in range(MATRIX_SIZE):
            for j in range(MATRIX_SIZE):
                for k in range(MATRIX_SIZE):
                    _val1 = get_index(i, j, k)

                    # left
                    for f in range(1, MATRIX_SIZE):
                        _tmp_j = j - f
                        if 0 <= _tmp_j < MATRIX_SIZE:
                            _val2 = get_index(i, _tmp_j, k)
                            _invalid += obj[_val1] * obj[_val2]

                    # up
                    for f in range(1, MATRIX_SIZE):
                        _tmp_i = i - f;
                        if 0 <= _tmp_i < MATRIX_SIZE:
                            _val2 = get_index(_tmp_i, j, k)
                            _invalid += obj[_val1] * obj[_val2]

        # area
        for area in range(MATRIX_SIZE):
            for num in range(MATRIX_SIZE):
                for index in range(MATRIX_SIZE - 1):
                    for index2 in range(index + 1, MATRIX_SIZE):
                        _val1 = convert_area_to_index(area, index, num)
                        _val2 = convert_area_to_index(area, index2, num)
                        _invalid += obj[_val1] * obj[_val2]

        ## remove invalid results
        if (_invalid > 0) or (_match > 0):
            print("Invalid: {}, Match: {}".format(str(_invalid), str(_match)))
            del number_place_out[:]
            continue
        else:
            return True
    return False

# displaying result
def dump_output():
    _row = 0
    for kk in range(len(number_place_out)):
        sys.stdout.write(str(number_place_out[kk]) + " ")
        _row += 1
        if (_row == MATRIX_SIZE):
            print("\n")
            _row = 0

#
# main function
#
def main():
    _simul = "qbsolv"
    _input_file_name = './input/input_example.csv'  # default file name
    _args = get_args()  # command line arguments

    if hasattr(_args, 'input'):
        if _args.input != None:
            _input_file_name = _args.input

    if hasattr(_args, 'sampler'):
        if _args.sampler != None:
            _simul = _args.sampler

    #
    # Parameter Definition
    #
    # h
    for i in range(MATRIX_SIZE * MATRIX_SIZE * MATRIX_SIZE):
        qubo[(i, i)] = -1.0 / QUBO_PARAM_FACTOR

    # J
    for i in range(MATRIX_SIZE):
        for j in range(MATRIX_SIZE):
            for k1 in range(MATRIX_SIZE - 1):
                for k2 in range(k1 + 1, MATRIX_SIZE):
                    _val1 = get_index(i, j, k1)
                    _val2 = get_index(i, j, k2)
                    if (_val1, _val2) in qubo:
                        qubo[(_val1, _val2)] += 1.0 / QUBO_PARAM_FACTOR
                    else:
                        qubo[(_val1, _val2)] = 1.0 / QUBO_PARAM_FACTOR

    # row & colomn
    for i in range(MATRIX_SIZE):
        for j in range(MATRIX_SIZE):
            for k in range(MATRIX_SIZE):
                _val1 = get_index(i, j, k)

                # left
                for f in range(1, MATRIX_SIZE):
                    _tmp_j = j - f
                    if 0 <= _tmp_j < MATRIX_SIZE:
                        _val2 = get_index(i, _tmp_j, k)
                        if (_val1, _val2) in qubo:
                            qubo[(_val2, _val1)] += 1.0 / QUBO_PARAM_FACTOR
                        else:
                            qubo[(_val2, _val1)] = 1.0 / QUBO_PARAM_FACTOR

                # up
                for f in range(1, MATRIX_SIZE):
                    _tmp_i = i - f
                    if 0 <= _tmp_i < MATRIX_SIZE:
                        _val2 = get_index(_tmp_i, j, k)
                        if (_val1, _val2) in qubo:
                            qubo[(_val2, _val1)] += 1.0 / QUBO_PARAM_FACTOR
                        else:
                            qubo[(_val2, _val1)] = 1.0 / QUBO_PARAM_FACTOR

    # area
    for area in range(MATRIX_SIZE):
        for num in range(MATRIX_SIZE):
            for index in range(MATRIX_SIZE - 1):
                for index2 in range(index + 1, MATRIX_SIZE):
                    _val1 = convert_area_to_index(area, index, num)
                    _val2 = convert_area_to_index(area, index2, num)
                    if (_val1, _val2) in qubo:
                        qubo[(_val1, _val2)] += 1.0 / QUBO_PARAM_FACTOR
                    else:
                        qubo[(_val1, _val2)] = 1.0 / QUBO_PARAM_FACTOR

    #
    # input (CSV format)
    #
    _x = 0
    _y = 0
    with open(_input_file_name, 'r') as f:
        _reader = csv.reader(f)
        for row in _reader:
            for e in row:
                number_place_in.append(int(e))
                if int(e) > 0:
                    _index = get_index(_y, _x, int(e) - 1)
                    # adjusting parameters
                    qubo[(_index, _index)] -= QUBO_PARAM_DELTA / QUBO_PARAM_FACTOR
                _x += 1
            _y += 1
            _x = 0

    _start = time.time()
    _ret = False
    # calculation
    for i in range(ITERATION_MAX):
        print("Try: {}".format(i + 1))
        _response = do_calculation(_simul)
        _result = list(_response.samples())

        # analysis
        if do_analysis(_result) != False:
            ## Result displaying
            dump_output()
            break

    _elapsed_time = time.time() - _start
    print ("elapsed_time:{} [sec]".format(_elapsed_time))
#
# execution
#
main()
