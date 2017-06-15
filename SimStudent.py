import re
import random
from math import fabs
from JRecInterface import JRecInterface

iteration = 200
num_exp = 100
rand = random.Random()

def sim_one_random(p):
    res = []
    interface = JRecInterface()
    for iter in range(iteration):
        interface.request()
        if rand.random() <= p:
            interface.response(True)
        else:
            interface.response(False)
        res.append(interface.recommender.num_colored())
    return res

def sim_random():
    ps = [0.1, 0.3, 0.5, 0.7, 0.9]
    for p in ps:
        r = []
        for i in xrange(num_exp):
            r.append(sim_one_random(p))
        r = [float(sum(r[i][iter] for i in xrange(num_exp))) / num_exp for iter in xrange(iteration)]
        print r

def dfs(p, gt_color, harders):
    for q in harders[p]:
        if gt_color[q] == -1:
            if gt_color[p] and rand.random() <= 0.3:
                gt_color[q] = True
            else:
                gt_color[q] = False
            dfs(q, gt_color, harders)

def sim_one_groundtruth():
    interface = JRecInterface()
    num = interface.recommender.knowledge.num()
    gt_color = [-1] * num
    score = [0] * num
    for p in range(num):
        if len(interface.recommender.knowledge.easiers[p]) == 0:
            gt_color[p] = (rand.random() <= 0.3)
            dfs(p, gt_color, interface.recommender.knowledge.harders)
    print float(sum([1 for p in gt_color if p])) / len(gt_color)
    for p in range(num):
        if gt_color[p]:
            for q in interface.recommender.knowledge.harders[p]:
                if not gt_color[q]:
                    score[q] = 1
    print sum([1 for p in gt_color if not p]), sum(score), len(gt_color)
    s = []
    for p in range(iteration):
        n = interface.request().num
        s.append(score[n])
        interface.response(gt_color[n])
        #print gt_color[n]
    return s

def sim_groundtruth():
    r = []
    for i in range(num_exp):
        r.append(sim_one_groundtruth())
    r = [float(sum(r[i][iter] for i in xrange(num_exp))) / num_exp for iter in xrange(iteration)]
    for i in range(1, iteration):
        r[i] = r[i] + r[i-1]
    print r

if __name__ == "__main__":
    sim_groundtruth()

######################################################################################################################

