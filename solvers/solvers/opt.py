import cvxpy as cp
import numpy as np
from time import time
import heapq
from problem.problem import get_model
from solvers.solver import call_solver
from util.util import Util


def solve_opt(d1, d2, d3, ruleNum, switchNum, w_r, M_w, rates, dep,
              depDict, links, dep_count, clients,
              select_pair, rule_sort_val, get_scores):
    objective, z_wv, y_rw, cntrs = get_model(d1, d2, d3, ruleNum, switchNum, w_r, M_w, rates, dep, links)
    prob = call_solver(objective, cntrs)
    print(prob.status, prob.value)

    if prob.status != "optimal":
        print("----", prob.status, prob.value)
        return -1

    # print_results(ruleNum, switchNum, depDict, z_wv, y_rw)
    return prob.value