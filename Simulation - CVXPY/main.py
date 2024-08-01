import cvxpy as cp
import numpy as np
from time import time
import heapq
from solvers.opt import solve_opt
from solvers.rexford import solve_rexford
from solvers.RaSe import solve_RaSe


def count_abs_dep(ruleNum, dep):
    dep_count = dict()
    for r in range(ruleNum):
        dep_count[r] = set()
        deps = np.nonzero(dep[r, :])[0]
        dep_count[r].update(deps)

    changed = True
    while changed:
        changed = False
        # print("Dept Count Compute...")
        for r1 in dep_count:
            for r2 in dep_count:
                if r2 in dep_count[r1]:
                    if len(dep_count[r2].difference(dep_count[r1])) > 0:
                        dep_count[r1].update(dep_count[r2])
                        changed = True

    # print("dep count={}".format(dep_count))
    return dep_count


def get_clients(ruleNum, dep):
    clients = dict()
    for r in range(ruleNum):
        clients[r] = set()
        deps = np.nonzero(dep[:, r])[0]
        clients[r].update(deps)

    changed = True
    while changed:
        changed = False
        # print("Dept Count Compute...")
        for r1 in clients:
            for r2 in clients:
                if r2 in clients[r1]:
                    if len(clients[r2].difference(clients[r1])) > 0:
                        clients[r1].update(clients[r2])
                        changed = True

    # print("dep count={}".format(dep_count))
    return clients


def main(in_itr):
    np.random.seed(in_itr)
    ruleNum = 100
    switchNum = 11
    d1 = 5
    d2 = 50
    d3 = 100

    links = np.zeros((switchNum, switchNum))
    abilene_topo = {
        0: [1,10], 1: [0,10,2], 2: [1,8,3], 3: [2,7,4], 4: [3,5],
        5: [4,6], 6: [5,7], 7: [3,8,6], 8: [2,9,7], 9: [10,8], 10: [0,1,9]
    }
    for i in abilene_topo:
        for j in abilene_topo[i]:
            links[i,j] = 1
    # print("links={}".format(links))

    # links = np.array([[0, 1, 2], [1, 0, 0], [1, 0, 0]])

    # specify the main switch for each rule
    switchRules = dict()
    w_r = np.zeros((ruleNum, switchNum))
    z_alpha = 1.1
    sw_ids = np.array(range(switchNum))
    np.random.shuffle(sw_ids)
    for r in range(ruleNum):
        wid = np.random.zipf(z_alpha)-1
        # wid = np.random.randint(low=0, high=switchNum)
        while wid >= switchNum:
            wid = np.random.zipf(z_alpha) - 1
        w = sw_ids[wid]
        w_r[r, w] = 1
        if w not in switchRules:
            switchRules[w] = list()
        switchRules[w].append(r)
    # print("switchRules: {}".format(switchRules))

    # specify the capacity of each switch
    M_w = np.random.randint(low=40, high=41, size=switchNum)
    # M_w = np.random.randint(low=100, high=501, size=switchNum)
    # M_w = np.random.randint(low=40, high=61, size=switchNum)
    # M_w = np.array([10, 50, 10, 10, 10, 50, 50, 50, 10, 10, 10])
    # print("M_w: {}".format(M_w))

    # M_w = np.array([1, 0, 200])

    # specify the rate of each rule
    rates = np.random.uniform(low=10, high=200, size=ruleNum)

    # specify the dependant of each rule
    # dependency is meaningful inside a switch
    depWindow = 6
    depSize = 4
    depDict = dict()
    dep = np.zeros((ruleNum, ruleNum))
    for w in range(switchNum):
        if not w in switchRules:
            continue
        for j in range(len(switchRules[w]) - 1):
            cwndIndex = j // depWindow
            r = switchRules[w][j]
            depDict[r] = set()
            # rand_d = np.random.choice(switchRules[w][j + 1:(cwndIndex*depWindow) + depWindow + 1], size=2)
            if j+1 < min(len(switchRules[w]), (cwndIndex*depWindow) + depWindow):
                rand_d = np.random.choice(range(j + 1, min(len(switchRules[w]), (cwndIndex*depWindow) + depWindow)), size=depSize)
                for d in rand_d:
                    dep[r, switchRules[w][d]] = 1
                    depDict[r].add(switchRules[w][d])
                # print("for {} = {}".format(r, depDict[r]))
        # last rule has no dependency
        depDict[switchRules[w][-1]] = set()
    # print("Deps: {}".format(depDict))
    # print("dep: {}".format(dep))

    dep_count = count_abs_dep(ruleNum, dep)
    # print("max dependency={} in list: {}".format(max([len(dep_count[r]) for r in dep_count]), dep_count))

    clients = get_clients(ruleNum, dep)
    # print("max clients={} in list: {}".format(max([len(clients[r]) for r in clients]), clients))

    funcs = {
        # "OPT": solve_opt,
        # "RXF": solve_rexford,
        "RaSe": solve_RaSe,
        "RG": solve_RaSe,
        "NC": solve_RaSe
    }
    select_pairs = {
        "OPT": None,
        "RXF": None,
        "RaSe": lambda x,y: np.argmax(x),
        "RG": lambda x,y: np.random.choice(np.nonzero(y)[0], size=1)[0],
        "NC": lambda x,y: np.random.choice(np.nonzero(y)[0], size=1)[0]
    }
    rule_sort_vals = {
        "OPT": None,
        "RXF": None,
        "RaSe": lambda x,y: x,
        "RG": lambda x,y: x,
        "NC": lambda x,y: 1
    }
    get_scoress = {
        "OPT": None,
        "RXF": None,
        "RaSe": lambda x,y: (x,y,1-x-y),
        "RG": lambda x,y: (2,1,0),
        "NC": lambda x,y: (2,0,1)
    }
    results = {}
    results_t = {}
    results_time = {}
    results_time_t = {}
    for f in funcs:
        t1 = time()
        print("run: ", f)
        res = funcs[f](d1, d2, d3, ruleNum, switchNum, w_r, M_w, rates, dep,
                       depDict, links, dep_count, clients,
                       select_pairs[f], rule_sort_vals[f], get_scoress[f])
        t2 = time()
        results_t[f] = res
        results_time_t[f] = (t2 - t1)
        if res < 0:
            print("{} was neg".format(f))
            return results, results_time

    for f in results_t:
        results[f] = results_t[f]
    for f in results_time_t:
        results_time[f] = results_time_t[f]

    print(results)
    print(results_time)
    return results, results_time


if __name__ == '__main__':
    itrNum = 3
    completedRounds = {}
    results = {}
    results_time = {}
    for itr in range(itrNum):
        result, result_time = main(itr)
        for f in result:
            if f not in results:
                results[f] = 0
                completedRounds[f] = 0
            completedRounds[f] += 1
            results[f] += result[f]
        for f in result_time:
            if f not in results_time:
                results_time[f] = 0
            results_time[f] += result_time[f]

    print("completed: {}".format(completedRounds))
    for f in results:
        print("{}={}".format(f, results[f]/completedRounds[f]))

    for f in results:
        print("{}={}".format(f, results_time[f]/completedRounds[f]))