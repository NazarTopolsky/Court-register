__author__ = 'n'
# TODO: non-unique chairman
import py2neo
from py2neo import Graph, Node, Relationship
from court_case import CourtCase

class Neo4jModel:
    def __init__(self):
        self.graph = Graph()

    def create(self):
        self.graph.schema.create_uniqueness_constraint("Region", "name")
        self.graph.schema.create_uniqueness_constraint("Court", "name")
        self.graph.schema.create_uniqueness_constraint("Court_Decision_Type", "name")
        self.graph.schema.create_uniqueness_constraint("Court_Judgement_Type", "name")
        self.graph.schema.create_uniqueness_constraint("Case", "id")
        self.graph.schema.create_uniqueness_constraint("Chairman", "name")

    def region(self, region_name):
        __region = self.graph.merge_one("Region", "name", region_name)
        __region.push()
        return __region

    def court(self, court_name, region_name):
        __court = self.graph.merge_one("Court", "name", court_name)
        __court.push()
        self.graph.create_unique(Relationship(__court, "SITUATED_IN", self.region(region_name)))
        return __court

    def chairman(self, chairman_name):
        __chairman = self.graph.merge_one("Chairman", "name", chairman_name)
        __chairman.push()
        return __chairman

    def decision_type(self, decision_type_name):
        __decision_type = self.graph.merge_one("Court_Decision_Type", "name", decision_type_name)
        __decision_type.push()
        return __decision_type

    def judgement_type(self, judgement_type_name):
        __judgement_type = self.graph.merge_one("Court_Judgement_Type", "name", judgement_type_name)
        __judgement_type.push()
        return __judgement_type

    def case(self, court_case, region_name):
        __case = self.graph.merge_one("Case", "id", court_case.decision_number)
        __case["reg_date"] = court_case.reg_date
        __case["law_date"] = court_case.law_date
        __case["link"] = court_case.link
        __case["text"] = court_case.text
        self.graph.create_unique(Relationship(__case, "RULED_BY", self.court(court_case.court_name, region_name)))
        self.graph.create_unique(Relationship(__case, "CARRIED_BY", self.chairman(court_case.chairman)))
        self.graph.create_unique(Relationship(__case, "OF_JUDGEMENT_TYPE", self.judgement_type(court_case.vr_type)))
        self.graph.create_unique(Relationship(__case, "OF_DECISION_TYPE", self.decision_type(court_case.cs_type)))
        __case.push()
        return __case
