from __future__ import annotations
from abc import ABC, abstractmethod, abstractproperty
from typing import Any
import pprint
from flask import Flask, jsonify
from nps_utils import *


class Builder(ABC):

    @abstractproperty
    def CustomerData(self) -> None:
        pass

    @abstractmethod
    def produce_dashboard(self, result) -> None:
        pass

    @abstractmethod
    def produce_customer_experience(self, result) -> None:
        pass

    @abstractmethod
    def produce_solutions_object(self, result) -> None:
        pass


class ConcreteDashboardBuilder(Builder):

    def produce_customer_experience(self) -> None:
        pass

    @property
    def CustomerData(self) -> None:
        pass

    def __init__(self) -> None:
        self._customerData = CustomerData()
        self.reset()

    def reset(self) -> None:
        pass

    @property
    def customerData(self) -> CustomerData:
        customer_data = self._customerData
        self.reset()
        return customer_data

    def produce_dashboard(self, result) -> None:
        self._customerData.add(result)

    def produce_reliability(self, result, name) -> None:
        self._customerData.buildReliability(result, name)

    def produce_availability(self, result) -> None:
        self._customerData.buildAvailability(result)

    def produce_response(self, result) -> None:
        self._customerData.buildResponseTime(result)

    def produce_customer_experience(self, result) -> None:
        self._customerData.buildCustomerExperience(result)

    def produce_activity_by_action(self, result, name) -> None:
        self._customerData.buildActivityByApi(result, name)

    def build_customer_satisfaction(self, result) -> None:
        self._customerData.buildCustomerSatisfaction(result)

    def build_NPS_score(self, result, name) -> None:
        self._customerData.buildNPSScore(result, name)

    def produce_solutions_object(self, result) -> None:
        self._customerData.add(result)


class CustomerData:
    """
    It makes sense to use the Builder pattern only when your products are quite
    complex and require extensive configuration.

    Unlike in other creational patterns, different concrete builders can produce
    unrelated products. In other words, results of various builders may not
    always follow the same interface.
    """

    def __init__(self) -> None:
        self.datas = []
        self.reliability = []
        self.availability = []
        self.response = []
        self.customer_satisfaction = []
        self.activity_by_api = []
        self.customer_experience = []
        self.nps_score = []

    def getReliabilityData(self):
        return self.reliability

    def getNPSScore(self):
        return self.nps_score

    def getCustomerSatisfaction(self):
        return self.customer_satisfaction

    def getCustomerExperience(self):
        return self.customer_experience

    def getActivityByApi(self):
        return self.activity_by_api

    def buildReliability(self, part: Any, name) -> None:
        print('Adding start-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        for i in part:
            if i in name:
                print(i)
                self.reliability.append(({i: part[i]}))
                self.datas.append(i)

    def buildAvailability(self, part: Any, name) -> None:
        print('Adding start-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        for i in part:
            if i in name:
                print(i)
                if i in name:
                    print(i)
                    self.availability.append(({i: part[i]}))
                    self.datas.append(i)

    def buildResponseTime(self, part: Any, name) -> None:
        print('Adding start-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        for i in part:
            if i in name:
                print(i)
                if i in name:
                    print(i)
                    self.response.append(({i: part[i]}))
                    self.datas.append(i)

    def buildCustomerExperience(self, part: Any, name) -> None:
        print('Adding start-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        for i in part:
            if i in name:
                print(i)
                if i in name:
                    print(i)
                    self.customer_experience.append(({i: part[i]}))
                    self.datas.append(i)

    def buildActivityByApi(self, part: Any, name) -> None:
        print('Adding start-----')
        print('buildNPSScore-----')
        self.activity_by_api = part

    def buildCustomerSatisfaction(self, part: Any, name) -> None:
        print('buildNPSScore-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        count = 0
        ok_status = 0
        if_status = 0
        uf_status = 0
        for i in part:
            for j in i['pivot']:
                for k in j:
                    pprint.pprint(j[k])
                    if str(j[k]) in name[0]:
                        ok_status = j['count']
                        print(ok_status)
                    if str(j[k]) in name[1]:
                        uf_status = j['count']
                        print(uf_status)
                    if str(j[k]) in name[2]:
                        if_status = j['count']
                        print(if_status)
                    self.datas.append(i)
            score = (ok_status/(uf_status+if_status+ok_status)) * 100
            self.customer_satisfaction.append(({i['field']: i['value'], 'score': score}))

    def buildNPSScore(self, part: Any, name) -> None:
        print('buildNPSScore-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        count = 0
        ok_status = 0
        if_status = 0
        uf_status = 0
        for i in part:
            for j in i['pivot']:
                for k in j:
                    pprint.pprint(j[k])
                    if str(j[k]) in name[0]:
                        ok_status = j['count']
                        print(ok_status)
                    if str(j[k]) in name[1]:
                        uf_status = j['count']
                        print(uf_status)
                    if str(j[k]) in name[2]:
                        if_status = j['count']
                        print(if_status)
                    self.datas.append(i)
            score = round((ok_status/(uf_status+if_status+ok_status)) * 100, 0)
            self.nps_score.append(({i['field']: i['value'], 'score': score}))
            self.customer_satisfaction.append(({i['field']: i['value'], 'score': score}))
            self.customer_experience.append(({i['field']: i['value'], 'score': score}))

    def list_data(self) -> None:
        # print(f"Product parts: {', '.join(self.datas)}", end="")
        print("Number of hits--: {0}".format(len(self.datas)))
        for i in self.datas:
            pprint.pprint(i)

    def populate_data(self) -> None:
        # print(f"Product parts: {', '.join(self.datas)}", end="")
        print("Number of hits: {0}".format(len(self.datas)))
        for i in self.datas:
            pprint.pprint(i)


class Director:

    def __init__(self) -> None:
        self._builder = None

    @property
    def builder(self) -> Builder:
        return self._builder

    @builder.setter
    def builder(self, builder: Builder) -> None:
        """
        The Director works with any builder instance that the client code passes
        to it. This way, the client code may alter the final type of the newly
        assembled product.
        """
        self._builder = builder

    def build_dashboard(self, result) -> None:
        return self.builder.produce_dashboard(result)

    def build_reliability(self, result, name) -> None:
        return self.builder.produce_reliability(result, name)

    def build_availability(self, result) -> None:
        return self.builder.produce_availability(result)

    def build_response(self, result) -> None:
        return self.builder.produce_response(result)

    def build_customer_satisfaction(self, result) -> None:
        self.builder.produce_customer_satisfaction(result)

    def build_activity_by_action(self, result, name) -> None:
        return self.builder.produce_activity_by_action(result, name)

    def build_customer_satisfaction(self, result) -> None:
        return self.builder.produce_customer_satisfaction(result)

    def build_NPS_score(self, result, name) -> None:
        return self.builder.build_NPS_score(result, name)

    def build_solutions(self, result) -> None:
        return self.builder.produce_solutions_object(result)

    def build_customer_experience(self, result) -> None:
        return self.builder.produce_customer_experience(result)
        # self.builder.produce_part_b()
        # self.builder.produce_part_c()


if __name__ == "__main__":
    director = Director()
    builder = ConcreteDashboardBuilder()
    director.builder = builder

    print("Standard basic product: ")
    director.build_dashboard()
    builder.customerData.list_data()

    print("\n")

    print("Standard full featured product: ")
    director.build_dashboard()
    builder.customerData.list_data()

    print("\n")

    # Remember, the Builder pattern can be used without a Director class.
    print("Custom product: ")
    builder.produce_customer_experience()
    builder.produce_solutions_object()
