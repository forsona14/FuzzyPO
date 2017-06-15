#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
from Article import Article
from FuzzyPORecommender import FuzzyPORecommender
from JRecResponse import JRecResponse
import nhk_easy
import nachrichtenleicht
import json

class JRecInterface:

    def __init__(self, recommender_json_str = None, lang=0):
        if lang == 1:
            # German
            self.articles = nachrichtenleicht.read_articles()
            self.recommender = FuzzyPORecommender(self.articles, recommender_json_str, lang)
        else:
            # Japanese
            self.articles = nhk_easy.read_articles()
            self.recommender = FuzzyPORecommender(self.articles, recommender_json_str, lang)


    def request(self):
        return self.recommender.request()

    def response(self, res):
        if type(res) == bool or type(res) == int or type(res) == float:
            res = JRecResponse(res)
        self.recommender.response(res)

    def recommender_json_str(self):
        return self.recommender.json_str()


