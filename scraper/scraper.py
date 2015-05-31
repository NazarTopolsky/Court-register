#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'n'

import requests
from html_parser import Parser
from court_case import CourtCase
from Neo4jModel import Neo4jModel
import traceback
import sys
from lxml import etree

regions = ['Автономна Республіка Крим', 'Волинська область', 'Вінницька область',
           'Дніпропетровська область', 'Донецька область', 'Дрогобицька область',
           'Житомирська область', 'Закарпатська область', 'Запорізька область',
           'Івано-Франківська область', 'Ізмаїльська область', 'Київська область',
           'Кіровоградська область', 'Луганська область', 'Львівська область',
           'Миколаївська область', 'Одеська область', 'Полтавська область',
           'Рівненська область', 'Сумська область', 'Тернопільська область',
           'Харківська область', 'Херсонська область', 'Хмельницька область',
           'Черкаська область', 'Чернівецька область', 'Чернігівська область',
           'м. Київ', 'м. Севастополь', 'ВС Центральний регіон',
           'ВС Західний регіон', 'ВС Південний регіон', 'ВС ВМС України']


def post_request(__url, __post_params):
    r = requests.post(__url, data=__post_params)
    return r.text


def to_dict(elem):
    res = dict()
    res['Decision'] = elem[0].find('a').text.strip() if elem[0] is not None else ''
    res['Link'] = 'http://www.reyestr.court.gov.ua/' + elem[0].find('a').text.strip() if elem[0] is not None else ''
    res['Text'] = ''
    res['VRType'] = elem[1].text.strip() if elem[1] is not None else ''
    res['RegDate'] = elem[2].text.strip() if elem[2] is not None else ''
    res['LawDate'] = elem[3].text.strip() if elem[3] is not None else ''
    res['CSType'] = elem[4].text.strip() if elem[4] is not None else ''
    res['CaseNumber'] = elem[5].text.strip() if elem[5] is not None else ''
    res['CourtName'] = elem[6].text.strip() if elem[6] is not None else ''
    res['ChairmanName'] = elem[8].text.strip() if elem[8] is not None else ''
    return res


class Scrapper:
    url = 'http://www.reyestr.court.gov.ua/'
    params = {'SearchExpression': '', 'CourtRegion[]': 4, 'UserCourtCode': '',
              'ChairmenName': '', 'RegNumber': '', 'RegDateBegin': '',
              'RegDateEnd': '', 'CaseNumber': '', 'ImportDateBegin': '',
              'ImportDateEnd': '', 'Sort': 0, 'PagingInfo.ItemsPerPage': 350,
              'Liga': 'true'}

    def __init__(self):
        res = []

    def scrap_one(self, region):
        res = []
        i = regions.index(region) + 2
        self.params['CourtRegion[]'] = i
        __raw_html = post_request(self.url, self.params)
        with open('html_dump', 'w') as f:
            f.write(__raw_html)
        p = Parser()
        elems = p.get_tds(__raw_html)
        # for e in elems:
        #     print(to_dict(e))
        # print(elems)
        del elems[0]
        for e in elems:
            res.append(CourtCase().from_dict(to_dict(e)))
        with open('dump_' + region, 'w') as f:
            for e in res:
                f.write(e.__str__() + '\n')
        return res

    # Handler is a method to handle each
    def scrap_brute(self, regions, handler, limit=100, dumpfile=None, logfile=None):
        dumpfile = dumpfile or {'filename': '', 'dump': False}
        if dumpfile['dump']:
            dump = open(dumpfile['filename'], 'w')
        logfile = logfile or {'filename': '', 'log': False}
        if logfile['log']:
            log = open(logfile['filename'], 'w')
        for reg in regions:
            for r in self.scrap_one(reg):
                try:
                    handler(r, reg)
                    if dumpfile['dump']:
                        dump.write(r)
                except BaseException as e:
                    log.write(str(e))


if __name__ == "__main__":
    s = Scrapper()
    n = Neo4jModel()
    f = open('log', 'w')
    # # n.case(result[0], 'Волинська область')
    for region in regions:

        for r in s.scrap_one(region):
            try:
                n.case(r, region)
            except BaseException as e:
                # print(str(e))
                f.write(str(e))
        print('Done: ' + region)
    f.close()
    # r = requests.get('http://www.reyestr.court.gov.ua/Review/36761656')
    # with open('html_dump', 'r') as f:
    #     text = f.read()
    # h = Parser().get_case(text)
    # with open('html_dump', 'w') as f:
    #     f.write(r.text)
    # with open('iframe', 'w') as f:
    #     f.write(etree.tostring(h[0]).decode("utf-8"))
    # print(h)
    # n.change_date()
