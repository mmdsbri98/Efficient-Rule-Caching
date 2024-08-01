import cvxpy as cp
import numpy as np
from time import time
import heapq
from problem.problem import get_model
from solvers.solver import call_solver
from util.util import Util


def solve_RaSe(d1, d2, d3, ruleNum, switchNum, w_r, M_w, rates,
                         dep, depDict, links, dep_count, clients,
                         select_pair, rule_sort_val, get_scores):
    objective, z_wv, y_rw, cntrs = get_model(d1, d2, d3, ruleNum, switchNum, w_r, M_w, rates, dep, links,
                                             relaxed=True)
    t1 = time()
    call_solver(objective, cntrs)
    t2 = time()
    print("solve 1: ", t2 - t1, len(cntrs))

    t1 = time()
    fix_pairs = np.ones((switchNum, switchNum))
    pairs = dict()
    for w in range(switchNum):
        v = select_pair(z_wv[w,:].value, links[w, :])
        fix_pairs[w, :] = np.zeros((1, switchNum))
        fix_pairs[w, v] = 1
        pairs[w] = v
        # call_solver(objective, cntrs + [z_wv <= fix_pairs])
    cntrs.append(z_wv >= fix_pairs)
    t2 = time()
    print("pairing: ", t2 - t1, len(cntrs))

    # objective2, z_wv2, y_rw2, cntrs2 = get_model(d1, d2, d3, ruleNum, switchNum, w_r, M_w, rates, dep, links,
    #                                          relaxed=True, div_by=1.0, fix_z=fix_pairs)
    # t1 = time()
    # prob = cp.Problem(cp.Minimize(objective), cntrs)
    # prob.solve(solver="SCIPY", warm_start=True, verbose=False)
    # t2 = time()
    # print("--->", t2 - t1, len(cntrs))

    t1 = time()
    rulesSorted = list()
    for r in range(ruleNum):
        rhoSum = rates[r]
        for rr in dep_count[r]:
            rhoSum += rates[rr]
        # rulesSorted.append((rhoSum/(1+len(dep_count[r])), r))
        rulesSorted.append((rule_sort_val(rhoSum, len(dep_count[r])), r))
    # print(rulesSorted)
    rulesSorted.sort(key=lambda x: x[0], reverse=True)
    t2 = time()
    print("sorting: ", t2 - t1, len(cntrs))

    cur_capacity = dict()
    placed = set()
    limitation = dict()
    y_rw_fix = np.ones((ruleNum, switchNum))
    for rv in rulesSorted:
        r = rv[1]
        if r in placed:
            continue
        w = np.argmax(w_r[r,:])
        v = pairs[w]
        # print(w,v)
        if w not in cur_capacity:
            cur_capacity[w] = M_w[w]
        if v not in cur_capacity:
            cur_capacity[v] = M_w[v]
        s = None
        w_score, v_score, ctrl_score = get_scores(y_rw[r,w].value, y_rw[r,v].value)
        # print("--{}, {}, {}".format(w_score, v_score, ctrl_score))
        if w_score >= max(v_score, ctrl_score) and cur_capacity[w] >= 1+len(dep_count[r]) \
                and (r not in limitation or limitation[r] == w):
            s = w
        elif v_score >= max(w_score, ctrl_score) and cur_capacity[v] >= 1+len(dep_count[r]) \
                and (r not in limitation or limitation[r] == v):
            s = v
        else:
            placed.add(r)
            y_rw_fix[r, :] = np.zeros((1, switchNum))
            if np.random.uniform(0, 1) < Util.SOLVE_PR:
                call_solver(objective, cntrs + [y_rw <= y_rw_fix])
            # y_rw_fix[r, w] = 0
            # y_rw_fix[r, v] = 0
            # cntrs.append(y_rw[r,w] == 0)
            # cntrs.append(y_rw[r,v] == 0)

        if s is not None:
            y_rw_fix[r, :] = np.zeros((1, switchNum))
            y_rw_fix[r, s] = 1
            # cntrs.append(y_rw[r, s] == 1)
            cur_capacity[s] = cur_capacity[s] - 1 - len(dep_count[r])
            placed.add(r)
            # t1 = time()
            for rr in clients[r]:
                limitation[rr] = s
            for rr in dep_count[r]:
                # cntrs.append(y_rw[rr, s] == 1)
                if rr not in placed:
                    placed.add(rr)
                    y_rw_fix[rr, :] = np.zeros((1, switchNum))
                    y_rw_fix[rr, s] = 1
                    for rrr in clients[rr]:
                        limitation[rrr] = s
            if np.random.uniform(0, 1) < Util.SOLVE_PR:
                call_solver(objective, cntrs + [y_rw <= y_rw_fix])
            # t2 = time()
            # print("l--->", t2 - t1)

        #if s is not None:
        #    prob = cp.Problem(cp.Minimize(objective), cntrs)
        #    prob.solve(solver="SCIPY", warm_start=True, verbose=False)

    # print("cur cap:{}".format(cur_capacity))
    # t1 = time()
    cntrs.append(y_rw <= y_rw_fix)
    # cntrs.append(y_rw >= y_rw_fix)
    prob = call_solver(objective, cntrs)
    # t2 = time()
    # print("--->", t2 - t1, len(cntrs))

    if prob.status != "optimal":
        return -1

    # print_results(ruleNum, switchNum, depDict, z_wv, y_rw)
    return prob.value