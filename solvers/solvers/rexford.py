import cvxpy as cp
import numpy as np
from time import time
import heapq
from problem.problem import get_model
from solvers.solver import call_solver
from util.util import Util


def solve_rexford(d1, d2, d3, ruleNum, switchNum, w_r, M_w, rates, dep,
                  depDict, links, dep_count, clients,
                  select_pair, rule_sort_val, get_scores):
    objective, z_wv, y_rw, cntrs = get_model(d1, d2, d3, ruleNum, switchNum, w_r, M_w, rates, dep, links, relaxed=False)
    call_solver(objective, cntrs)

    pairs_cntr = np.zeros((switchNum, switchNum))
    pairs = dict()
    for w in range(switchNum):
        neighbors = np.nonzero(links[w, :])
        pair = np.random.choice(neighbors[0], size=1)
        pairs_cntr[w, pair] = 1
        pairs[w] = pair[0]
    cntrs.append(z_wv >= pairs_cntr)
    prob = call_solver(objective, cntrs)

    if prob.status != "optimal":
        return -1

    # print_results(ruleNum, switchNum, depDict, z_wv, y_rw)
    return prob.value