#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'n'

from lxml import html, etree

class Parser:
    def __init__(self):
        self.tree = None
        self.xpath = 'div[@id="divresult"]/text()'

    def get_tds(self, raw_data):
        res = []
        self.tree = html.fromstring(raw_data)
        # el1: div_login, el2: div_divresult, el3: each tr in table
        for el1 in self.tree.find('body').find('div').find('div'):
            if el1.text is not None and el1.get('id') == 'login':
                for el2 in el1:
                    if el2.text is not None and el2.get('id') == 'divresult':
                        for el3 in el2.find('table'):
                            print(el3.body)
                            res.append(el3)
        return res

    def get_case(self, raw_data):
        res = dict()
        self.tree = html.fromstring(raw_data)
        res = self.tree.xpath('//textarea')
        return res

    def to_dict(self, elem):
        res = dict()
        res['Decision'] = elem[0].find('a').text.strip() if elem[0] is not None else ''
        res['Link'] = 'http://www.reyestr.court.gov.ua/' + elem[0].find('a').text.strip()
        res['Text'] = ''
        res['VRType'] = elem[1].text.strip()
        res['RegDate'] = elem[2].text.strip()
        res['LawDate'] = elem[3].text.strip()
        res['CSType'] = elem[4].text.strip()
        res['CaseNumber'] = elem[5].text.strip()
        res['CourtName'] = elem[6].text.strip()
        res['ChairmanName'] = elem[8].text.strip()
        return res

    def feed(self, raw_data):
        self.tree = html.fromstring(raw_data)
        return self.tree
