import blueqat
import numpy as np

class RulloSolver:
    def __init__(self, _size):
        self.size = _size   # the size of problem: size x size

    def _checkResult(self, _result):
        ret = 0
        for i in range(self.size):
            sum = 0
            for j in range(self.size):
                sum += _result[i][j] * self.area[i][j]
            ret += (sum - self.row[i])**2
        for j in range(self.size):
            sum = 0
            for i in range(self.size):
                sum += _result[i][j] * self.area[i][j]
            ret += (sum - self.column[j])**2
        return (ret == 0)

    def setProblem(self, _area, _row, _column):
        if len(_area) != self.size:
            return False

        for arr in _area:
            if len(arr) != self.size:
                return False

        if len(_row) != self.size or len(_column) != self.size:
            return False

        self.area = _area
        self.row = _row
        self.column = _column
        return True

    def solve(self, _iteration):
        a = blueqat.opt.opt()
        Q = np.array([[0.0 for i in range(self.size * self.size)] for j in range(self.size * self.size)])
        
        # h
        for i in range(self.size):
            for j in range(self.size):
                Q[self.size * i + j][self.size * i + j] = self.area[i][j] * (self.area[i][j] - self.row[i] - self.column[j])

        # J
        for i in range(self.size):
            for j1 in range(self.size-1):
                for j2 in range(j1+1, self.size):
                    Q[self.size * i + j1][self.size * i + j2] += self.area[i][j1] * self.area[i][j2]

        for j in range(self.size):
            for i1 in range(self.size-1):
                for i2 in range(i1+1, self.size):
                    Q[self.size * i1 + j][self.size * i2 + j] += self.area[i1][j] * self.area[i2][j]

        a.qubo = Q
        ret = a.sa(shots=_iteration, sampler="fast")
        for result in ret:
            twodim = np.reshape(result, (self.size, self.size))
            print(twodim)
            validity = self._checkResult(twodim)
            print(validity)
            if validity != False:
                return twodim
        return []
       
if __name__ == '__main__':
    solver = RulloSolver(4)

    TBL_ROW = np.array([10, 20, 7, 6])
    TBL_COL = np.array([11, 9, 15, 8])
    TBL_CELL = np.array([[6, 3, 4, 2], [4, 8, 4, 8], [1, 5, 7, 1], [5, 1, 6, 3]])

    ret = solver.setProblem(TBL_CELL, TBL_ROW, TBL_COL)
    if ret != True:
        print("Failed to set problem...")

    ret = solver.solve(30)
    print("ret={}".format(ret))
