import cvxpy as cp
from util.util import Util


def call_solver(objective, cntrs):
    prob = cp.Problem(cp.Minimize(objective), cntrs)
    if Util.SOLVER == "MOSEK":
        if Util.TIME_LIMIT > 0:
            mosek_params = {'MSK_DPAR_OPTIMIZER_MAX_TIME': Util.TIME_LIMIT}
            prob.solve(solver=cp.MOSEK, warm_start=True, verbose=False, mosek_params=mosek_params)
        else:
            prob.solve(solver=cp.MOSEK, warm_start=True, verbose=False)
    else:
        prob.solve(solver=cp.SCIPY, warm_start=True, verbose=False)
    return prob


