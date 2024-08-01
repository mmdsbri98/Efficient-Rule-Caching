import cvxpy as cp
import numpy as np
from time import time
import heapq
from util.util import Util


def get_model(d1, d2, d3, ruleNum, switchNum, w_r, M_w, rates, dep, links, relaxed=False):
    # variables
    z_wv = cp.Variable((switchNum, switchNum), boolean=not relaxed)
    y_rw = cp.Variable((ruleNum, switchNum), boolean=not relaxed)

    # constraints
    cntrs = list()

    if relaxed:
        cntrs.append(z_wv <= np.ones((switchNum, switchNum)))
        cntrs.append(z_wv >= np.zeros((switchNum, switchNum)))
        cntrs.append(y_rw <= np.ones((ruleNum, switchNum)))
        cntrs.append(y_rw >= np.zeros((ruleNum, switchNum)))

    # don't pair with itself
    cntrs.append(z_wv <= np.ones((switchNum, switchNum)) - np.eye(switchNum))
    # don't pair with non-neighbors
    cntrs.append(z_wv <= links)
    # have one pair
    cntrs.append(cp.sum(z_wv, axis=1) == np.ones(switchNum))
    # put only on main or pair
    cntrs.append(y_rw <= w_r + w_r @ z_wv)
    # put on at most one switch
    cntrs.append(cp.sum(y_rw, axis=1) <= np.ones(ruleNum))
    # switch mem capacity
    cntrs.append(cp.sum(y_rw, axis=0) <= M_w)
    # put dependants on the same switch
    # only when a rule has dependency
    depAux = np.repeat(np.sum(dep, axis=1).reshape((ruleNum, 1)), switchNum, axis=1)
    # print("depAux: {}".format(depAux))
    cntrs.append(cp.multiply(y_rw, depAux) <= dep @ y_rw)

    # objective = d1 * cp.sum(cp.multiply(cp.sum(cp.multiply(y_rw, w_r), axis=1), rates)) + \
    #             d2 * (
    #                     cp.sum(cp.multiply(cp.sum(y_rw, axis=1), rates))
    #                     - cp.sum(cp.multiply(cp.sum(cp.multiply(y_rw, w_r), axis=1), rates))
    #             ) + \
    #             d3 * (
    #                     np.sum(rates)
    #                     - cp.sum(cp.multiply(cp.sum(y_rw, axis=1), rates))
    #                     - cp.sum(cp.multiply(cp.sum(cp.multiply(y_rw, w_r), axis=1), rates))
    #             )
    objective = (d1 - d3) * cp.sum(cp.multiply(cp.sum(cp.multiply(y_rw, w_r), axis=1), rates)) + \
                (d2 - d3) * cp.sum(cp.multiply(cp.sum(cp.multiply(y_rw, np.ones((ruleNum, switchNum)) - w_r), axis=1), rates)) + \
                d3 * np.sum(rates)
    return objective, z_wv, y_rw, cntrs
