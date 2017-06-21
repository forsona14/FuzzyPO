import re
import random
from math import fabs
from JRecInterface import JRecInterface

iteration = 200
num_exp = 30
rand = random.Random()

def direct(k):
    n = k.num()
    direct_easier_graph = [[False] * n for i in range(n)]
    for p in range(n):
        for q in k.harders[p]:
            direct_easier_graph[p][q] = True
            for t in k.harders[p]:
                if q != t and k.easier_graph[t][q]:
                    direct_easier_graph[p][q] = False
                    break
    #k.easier_graph = direct_easier_graph
    #k.easiers = [set([j for j in range(n) if k.easier_graph[j][i] and i != j]) for i in range(n)]
    #k.harders = [set([j for j in range(n) if k.easier_graph[i][j] and i != j]) for i in range(n)]
    return [set([j for j in range(n) if direct_easier_graph[i][j] and i != j]) for i in range(n)]

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

def dfs(p, gt_color, harders, sim_para):
    for q in harders[p]:
        if gt_color[q] == -1:
            if gt_color[p] and rand.random() <= sim_para:
                gt_color[q] = True
            else:
                gt_color[q] = False
            dfs(q, gt_color, harders, sim_para)
        # continue
        if gt_color[q] == True and gt_color[p] == False:
            gt_color[q] = False
            dfs(q, gt_color, harders, sim_para)


def sim_one_groundtruth(sim_para, balance):
    interface = JRecInterface(lang=1)
    interface.recommender.global_local_balance = balance
    direct(interface.recommender.knowledge)
    num = interface.recommender.knowledge.num()
    gt_color = [-1] * num
    score = [0] * num
    for p in range(num):
        if len(interface.recommender.knowledge.easiers[p]) == 0:
            gt_color[p] = (rand.random() <= sim_para)
            dfs(p, gt_color, interface.recommender.knowledge.harders, sim_para)
    for p in range(num):
        for q in interface.recommender.knowledge.harders[p]:
            if not gt_color[p] and gt_color[q]:
                print "Error!"
    # print float(sum([1 for p in gt_color if p])) / len(gt_color)

    direct_harders = direct(interface.recommender.knowledge)
    for p in range(num):
        if gt_color[p]:
            #for q in interface.recommender.knowledge.harders[p]:
            for q in direct_harders[p]:
                if not gt_color[q] and interface.recommender.knowledge.intersection_graph[p][q] > len(interface.recommender.knowledge.data[q].data) * 0.5:
                    score[q] = 1
    #print sum([1 for p in gt_color if not p]), sum(score), len(gt_color)
    s = []
    for p in range(iteration):
        n = interface.request().num
        s.append(score[n])
        interface.response(gt_color[n])
        #print gt_color[n]
    return s

def sim_groundtruth(sim_para, balance):
    r = []
    for i in range(num_exp):
        r.append(sim_one_groundtruth(sim_para, balance))
    r = [float(sum(r[i][iter] for i in xrange(num_exp))) / num_exp for iter in xrange(iteration)]
    for i in range(1, iteration):
        r[i] = r[i] + r[i-1]
    print "Sim_para =", sim_para, "      Balance =", balance
    print ', '.join([str(i) for i in r])

if __name__ == "__main__":
    for sim_para in [0.3, 0.66, 0.89]:  # 0.3=20%, 0.66=50%, 0.89=80%, 0.95=90%
        for balance in [5.0, 50.0, 500000000.0]:
            sim_groundtruth(sim_para, balance)

######################################################################################################################

