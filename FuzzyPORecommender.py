#!/usr/bin/python
# -*- coding: UTF-8 -*-

from JRecRequest import JRecRequest
from random import *
from Knowledge import *
from collections import Counter
import json
from math import sqrt, pow
#import numpy

FuzzyPORecommender_Version = 20170522

PSEODO_COUNT = 1.1

class FuzzyPORecommender:
    def __init__(self, articles, json_str = None, lang=0, global_local_balance=5.0):
        self.articles = articles
        self.knowledge = Knowledge(articles, 0.8, lang)
        self.N = len(self.knowledge.data)
        self.random = Random()

        # TODO: put it into Serialized Part
        self.global_local_balance = global_local_balance
        # Global Only:     large number 500000000.0
        # Global + Local:  50.0
        # Local Only:      5.0

    ##########################################################
    ## Serialized Part
        if json_str != None:
            _l = json.loads(json_str)
        else:
            _l = []
        if len(_l) != 5:
        # if json_str == None or l[0] != FuzzyPORecommender_Version
            self.version = FuzzyPORecommender_Version
            self.request_history = []
            self.request_info_history = []
            self.response_history = []
            self.color = [-1] * self.N  # -1 for unknown, or [0,1]
        else:
            self.version = _l[0]
            self.request_history = _l[1]
            self.request_info_history = _l[2]
            self.response_history = _l[3]
            self.color = _l[4]

        ##########################################################
        ## Aux Part
        #self.easiers = [set([j for j in xrange(self.N) if self.knowledge.easier_graph[j][i] and i != j]) for i in xrange(self.N)]
        #self.harders = [set([j for j in xrange(self.N) if self.knowledge.easier_graph[i][j] and i != j]) for i in xrange(self.N)]

    def json_str(self):
        return json.dumps([self.version, self.request_history, self.request_info_history, self.response_history, self.color])

    # Expected Gain (number of nodes that can be colored) after Asking one doc to the student
    def color_gain(self, id, alpha=0.5):
        color_easier = sum(1 for i in self.knowledge.easiers[id] if self.color[i] == -1)
        color_harder = sum(1 for i in self.knowledge.harders[id] if self.color[i] == -1)
        return 1 + (1.0 - alpha) * color_easier + alpha * color_harder
        #return 1 + min ((1.0 - alpha) * color_easier, alpha * color_harder)
        #return 1
        #p = 0.5
        #return pow(pow((1.0 - alpha) * color_easier + 1, p) + pow(alpha * color_harder + 1, p), 1.0/p)

    # Color one node and all related node(s)
    def color_node(self, id, res):
        if res == True:
            self.color[id] = 1
            for i in self.knowledge.easiers[id]:
                if self.color[i] == -1:
                    self.color[i] = 1
        elif res == False:
            self.color[id] = 0
            for i in self.knowledge.harders[id]:
                if self.color[i] == -1:
                    self.color[i] = 0

    def cut_gain(self, id, alpha=0.5):

        if len(self.knowledge.easiers[id]) == 0:
            return 1
        else:
            return 1 + sum([1 for i in self.knowledge.easiers[id] if self.color[i] == 1]) # and self.knowledge.intersection_graph[id][i] > len(self.knowledge.data[i].data) * 0.5])

        new_colored = [i for i in self.knowledge.easiers[id] if self.color[i] == -1]
        new_colored.append(id)
        new_cut = set([])
        for nc in new_colored:
            for i in self.knowledge.harders[nc]:
                if self.color[i] == 0:
                    new_cut.add(i)
        new_cut_1 = len(new_cut)

        new_colored = [i for i in self.knowledge.harders[id] if self.color[i] == -1]
        new_colored.append(id)
        new_cut = set([])
        for nc in new_colored:
            for i in self.knowledge.easiers[nc]:
                if self.color[i] == 1:
                    new_cut.add(i)
        new_cut_2 = len(new_cut)

        #return (1.0 - alpha) * new_cut_1 + alpha * new_cut_2
        return new_cut_2

    def random_select(self, random_num, max_ids, max_values):
        if random_num < len(max_values):
            random_num = len(max_values)
        if random_num == 1:
            return max_ids[0]
        s = sum(max_values[:random_num])
        #return numpy.random.choice(max_ids[:random_num], p=[float(i)/s for i in max_values[:random_num]])

    def color_gain_request(self):

        ####################################################
        # Calculation for Adaptivity
        color_stats = {0:0, 1:0}
        for i in range(self.N):
            if self.color[i] == 0 or self.color[i] == 1:
                color_stats[self.color[i]] += 1
        alpha_1 = (PSEODO_COUNT + color_stats[0]) / (2 * PSEODO_COUNT + color_stats[1] + color_stats[0])

        response_history_stats = {0:0, 1:0}
        for r in self.response_history:
            if r == True:
                response_history_stats[1] += 1
            elif r == False:
                response_history_stats[0] += 1
        alpha_2 = (PSEODO_COUNT + response_history_stats[0]) / (2 * PSEODO_COUNT + response_history_stats[1] + response_history_stats[0])

        alpha = alpha_2
        #print alpha

        ##############################################################################################
        color_gains = {id:self.color_gain(id, alpha) for id in range(self.N) if self.color[id] == -1}
        if len(color_gains) == 0:
            return
        max_color_gain = max(color_gains.values())
        max_color_gain_ids = [id for id in color_gains.keys() if color_gains[id] == max_color_gain]
        self.random.shuffle(max_color_gain_ids)
        # print "Color:", max_color_gain, max_color_gain_ids[0]
        self.request_history.append(self.knowledge.data[max_color_gain_ids[0]].doc_id)
        self.request_info_history.append("Assessment(Global Search)")

    def cut_gain_request(self):

        #### TODO If use Adabptivity here, remember to change according to color_gain_request()
        response_history_stats = {0:0, 1:0}
        for i in range(self.N):
            if self.color[i] == 0 or self.color[i] == 1:
                response_history_stats[self.color[i]] += 1
        alpha = (PSEODO_COUNT + response_history_stats[0]) / (PSEODO_COUNT + response_history_stats[1] + response_history_stats[0])
        alpha = 0.5
        ###########################################################

        cut_gains = {id:self.cut_gain(id, alpha) for id in range(self.N) if self.color[id] == -1}
        if len(cut_gains) == 0:
            return
        max_cut_gain = max(cut_gains.values())
        max_cut_gain_ids = [id for id in cut_gains.keys() if cut_gains[id] == max_cut_gain]
        # print max_cut_gain, len(max_cut_gain_ids)
        self.random.shuffle(max_cut_gain_ids)
        self.request_history.append(self.knowledge.data[max_cut_gain_ids[0]].doc_id)
        # print "Cut:", max_cut_gain, max_cut_gain_ids[0]
        self.request_info_history.append("Recommendation(Local Search)")

    def recommendation_request(self):
        candidate = {}
        for i in range(self.N):
            if self.color[i] == 1:
                for j in self.knowledge.harders[i]:
                    if self.color[j] == -1:
                        aug = float(len(self.knowledge.data[j].data)) / float(self.knowledge.intersection_graph[i][j])
                        if not candidate.has_key(j) or candidate[j] < aug:
                            candidate[j] = aug
        if len(candidate) == 0:
            return
        min_aug = min(candidate.values())
        candidates = [k for k in candidate.keys() if candidate[k] == min_aug]
        self.random.shuffle(candidates)
        # print "R:", min_aug, candidates[0]
        self.request_history.append(self.knowledge.data[candidates[0]].doc_id)

    def request(self):
        if len(self.response_history) < len(self.request_history):
            return JRecRequest(self.articles[self.request_history[-1]], num=len(self.request_history), info=self.request_info_history[-1])
        #TODO Trade-off
        t = len(self.request_history)
        if t > 5 and self.random.random() < float(t) / self.global_local_balance:
            #self.recommendation_request()
            #print "Cut"
            self.cut_gain_request()
        else:
            #self.assessment_request()
            #print "Color"
            self.color_gain_request()
        if len(self.response_history) < len(self.request_history):
            return JRecRequest(self.articles[self.request_history[-1]], num=len(self.request_history), info=self.request_info_history[-1])
        else:
            return None

    def response(self, response):
        self.color_node(self.knowledge.doc_id_to_id[self.request_history[-1]], response.understood)
        self.response_history.append(response.understood)

    def num_colored(self):
        return sum(1 for i in range(self.N) if self.color[i] != -1)

    def color_stats(self):
        stats = {0:0, 1:0}
        for i in range(self.N):
            if self.color[i] == 0 or self.color[i] == 1:
                stats[self.color[i]] += 1
        return stats