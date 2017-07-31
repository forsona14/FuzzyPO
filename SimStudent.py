import re
import random
from math import fabs
from JRecInterface import JRecInterface

iteration = 200
num_exp = 1000
rand = random.Random()
new_easier_graph = []
new_easiers = []
new_harders = []
new_direct_easiers = []
new_direct_harders = []

def to_binarytree(k):
    n = k.num()
    new_easier_graph = [[False] * n for i in range(n)]
    pool = range(n)
    random.shuffle(pool)
    for i in range(1,n):
        j = i
        while j > 0:
            j = (j-1) / 2
            new_easier_graph[pool[i]][pool[j]] = True
    k.easier_graph = new_easier_graph
    k.easiers = [set([j for j in range(n) if k.easier_graph[j][i] and i != j]) for i in range(n)]
    k.harders = [set([j for j in range(n) if k.easier_graph[i][j] and i != j]) for i in range(n)]

def to_1d(k):
    global new_easier_graph, new_easiers, new_harders, new_direct_easiers, new_direct_harders
    n = k.num()
    if new_easier_graph == []:
        new_easier_graph = [[False] * n for i in range(n)]
        pool = range(n)
        random.shuffle(pool)
        for i in range(1,n):
            for j in range(i):
                new_easier_graph[pool[i]][pool[j]] = True
        new_easiers = [set([j for j in range(n) if new_easier_graph[j][i] and i != j]) for i in range(n)]
        new_harders = [set([j for j in range(n) if new_easier_graph[i][j] and i != j]) for i in range(n)]
        new_direct_easiers = [[] for i in range(n)]
        new_direct_harders = [[] for i in range(n)]
        for i in range(1,n):
            new_direct_easiers[pool[i-1]].append(pool[i])
            new_direct_harders[pool[i]].append(pool[i-1])
    k.easier_graph = new_easier_graph
    k.easiers = new_easiers
    k.harders = new_harders
    k.direct_easiers = new_direct_easiers
    k.direct_harders = new_direct_harders

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
    interface = JRecInterface(lang=0)
    interface.recommender.global_local_balance = balance
    #direct(interface.recommender.knowledge)
    num = interface.recommender.knowledge.num()
    gt_color = [-1] * num
    score = [0] * num

    ##################################
    ##################################
    # Mannually Change Easier Graph Here
    # Test Different Shape


    #to_binarytree(interface.recommender.knowledge)




    # to_1d(interface.recommender.knowledge)
    # p = rand.randint(0,num-1)
    # gt_color = [False] * num
    # gt_color[p] = True
    # for j in interface.recommender.knowledge.easiers[p]:
    #     gt_color[j] = True

    ##################################
    ##################################

    ##################################
    # TODO:Remember to uncomment if not using makeup graphs
    for p in range(num):
       if len([q for q in interface.recommender.knowledge.easiers[p] if not interface.recommender.knowledge.easier_graph[p][q]]) == 0:
           gt_color[p] = (rand.random() <= sim_para)
           dfs(p, gt_color, interface.recommender.knowledge.harders, sim_para)
    ##################################

    #for p in range(num):
    #    if gt_color[p] == -1:
    #        print "Color Not Complete."
    ##################################

    ##################################
    #for p in range(num):
    #    if gt_color[p] == -1:
    #        gt_color[p] = (rand.random() <= sim_para)
    #        if gt_color[p]:
    #            for q in interface.recommender.knowledge.easiers[p]:
    #                if gt_color[q] == -1:
    #                    gt_color[q] = True
    #        else:
    #            for q in interface.recommender.knowledge.harders[p]:
    #                if gt_color[q] == -1:
    #                    gt_color[q] = False
    ##################################
    #for p in range(num):
    #    for q in interface.recommender.knowledge.harders[p]:
    #        if not gt_color[p] and gt_color[q]:
    #            print "Error!"
    #print float(sum([1 for p in gt_color if p])) / len(gt_color)

    #direct_harders = direct(interface.recommender.knowledge)
    direct_harders = interface.recommender.knowledge.direct_harders
    for p in range(num):
        if gt_color[p]:
            #for q in interface.recommender.knowledge.harders[p]:
            for q in direct_harders[p]:
                if not gt_color[q]: # and interface.recommender.knowledge.intersection_graph[p][q] > len(interface.recommender.knowledge.data[q].data) * 0.5:
                    score[q] = 1
                    #print "*:", p, q
    #print sum([1 for p in gt_color if not p]), sum(score), len(gt_color)

    s = []
    for p in range(iteration):
        req = interface.request()
        if req == None:
            s.append(0)
            continue
        doc_id = req.doc_id
        n = interface.recommender.knowledge.doc_id_to_id[doc_id]
        if interface.recommender.knowledge.data[n].doc_id != doc_id:
            print "Doc_id_to_id Error!"
        # print n, doc_id, gt_color[n]
        #print n, len(interface.recommender.knowledge.easiers[n])
        s.append(score[n])
        interface.response(gt_color[n])
        #print gt_color[n]

    #print "_____________________"
    return s

def sim_groundtruth(sim_para, balance):
    print "Sim_para =", sim_para, "      Balance =", balance, "     ",
    r = []
    for i in range(num_exp):
        r.append(sim_one_groundtruth(sim_para, balance))
        if (i+1)%10==0:
            print i+1,
    r = [float(sum(r[i][iter] for i in xrange(num_exp))) / num_exp for iter in xrange(iteration)]
    for i in range(1, iteration):
        r[i] = r[i] + r[i-1]
    print
    print ' '.join([str(i) for i in r])

if __name__ == "__main__":
#    for sim_para in [0.98, 0.95, 0.89, 0.32, 0.67, 0.89]:  # 0.32=20%, 0.67=50%, 0.89=80%, 0.95=90%
    for sim_para in [0.32, 0.67, 0.89, 0.98]:
#     for sim_para in [0]:                # Used for make-up graphs without sim_para
        for balance in [0.5, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 500.0, 500000000.0]:
#        for balance in [20.0, 100.0, 150.0]:
#        for balance in [50.0]:
            sim_groundtruth(sim_para, balance)

######################################################################################################################

