# Rullo Solver
Rullo is the puzzle game changing status of cells with number to match sum of each row & column to the specified numbers. A script solves the puzzle with the quantum computation simulator [Blueqat](https://github.com/Blueqat/Blueqat).

## How to use
You have to install `Blueqat` (see [README](https://github.com/Blueqat/Blueqat) for details).

* Problem table

    ```python
    """
        A case with 4x4 problem
        
             6  3  4  2 | 10
             4  8  4  8 | 20
             1  5  7  1 |  7
             5  1  6  3 |  6
            -- -- -- -- 
            11  9 15  8
    """
    TBL_ROW  = np.array([10, 20, 7, 6])
    TBL_COL  = np.array([11, 9, 15, 8])
    TBL_CELL = np.array([[6, 3, 4, 2], [4, 8, 4, 8], [1, 5, 7, 1], [5, 1, 6, 3]])
    ```

* Solving

    ```python
    # create instance
    solver = RulloSolver(4)

    # set problem table
    ret = solver.setProblem(TBL_CELL, TBL_ROW, TBL_COL)
    if ret != True:
        print("Failed to set problem...")

    # solve (argument is iteration number of simulation)
    ret = solver.solve(30)
    print("ret={}".format(ret))
```