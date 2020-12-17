from __future__ import annotations
from abc import ABC, abstractmethod, abstractproperty
from typing import Any
import pprint
from flask import Flask, jsonify
from nps_utils import *
from copy import deepcopy
from reliability.Reliability_testing import one_sample_proportion
import datetime


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

    def produce_availability(self, result, name) -> None:
        self._customerData.buildAvailability(result, name)

    def produce_response(self, result, name) -> None:
        self._customerData.buildResponseTime(result, name)

    def produce_customer_experience(self, result, name) -> None:
        self._customerData.buildCustomerExperience(result, name)

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
        self.previous_months = []
        self.current_months = []
        self.customer_experience = []
        self.nps_score = []

    def getReliabilityData(self):
        return self.reliability

    def getResponseData(self):
        return self.response

    def getAvailabilityData(self):
        return self.availability

    def getNPSScore(self):
        return self.nps_score

    def getCustomerSatisfaction(self):
        return self.customer_satisfaction

    def getActivityByApi(self):
        return self.activity_by_api

    def getCustomerExperience(self):
        month_array = {}
        for months in self.previous_months:
            datestr = None
            for key in months:
                if key in 'score':
                    scorekey = 'score'
                    for current in self.current_months:
                        day_str = datestr[0:2]
                        if day_str not in self.customer_experience:
                            self.customer_experience.append(({'Day': day_str, 'PreviousMonth': months[scorekey],
                                                              'CurrentMonth': current[scorekey]}))
                else:

                    datestr = key.split('-')[2]
        return self.customer_experience

    def buildReliability(self, part: Any, name) -> None:
        count = 0
        ok_status = {}
        if_status = {}
        uf_status = {}
        print("print reliability---------------")
        print(part)
        for i in part:
            for ii in i:
                if ii in 'ranges':
                    data_count_str = None
                    data_count = 0
                    for m in i['ranges']['date']['counts']:
                        if isinstance(m, int):
                            data_count = m
                        else:
                            data_count_str = str(m)
                            if str(i['value']) in 'OK':
                                ok_status[data_count_str] = data_count
                            if str(i['value']) in 'UF':
                                uf_status[data_count_str] = data_count
                            if str(i['value']) in 'IF':
                                if_status[data_count_str] = data_count
                            data_count_str = None
        for ok_key in ok_status.keys():
            total_count = uf_status[ok_key] + if_status[ok_key] + ok_status[ok_key]
            result = one_sample_proportion(trials=total_count, successes=ok_status[ok_key])
            self.current_months.append(({ok_key: result}))

    def buildAvailability(self, part: Any, name) -> None:
        print('Adding start-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        for i in part:
            for j in i:
                if j in name and i not in self.availability:
                    self.availability.append(deepcopy(i))
                    self.datas.append(deepcopy(i))

    def buildResponseTime(self, part: Any, name) -> None:
        print('Adding start-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        seconds = 0
        milliseconds = 1000
        for i in part['facets']['date']:
            for j in part['facets']['date'][i]:
                if j in name:
                    response = part['facets']['date'][i][j]
                    print(response)
                    seconds = round(response / milliseconds, 6)
                    self.response.append({'x': i, 'y': seconds})

    def buildCustomerExperience(self, part: Any, name) -> None:
        count = 0
        ok_status = {}
        if_status = {}
        uf_status = {}
        for i in part['status']:
            for ii in i:
                if ii in 'ranges':
                    data_count_str = None
                    data_count = 0
                    for m in i['ranges']['date']['counts']:
                        if isinstance(m, int):
                            data_count = m
                        else:
                            data_count_str = str(m)
                            if str(i['value']) in 'OK':
                                ok_status[data_count_str] = data_count
                            if str(i['value']) in 'UF':
                                uf_status[data_count_str] = data_count
                            if str(i['value']) in 'IF':
                                if_status[data_count_str] = data_count
                            data_count_str = None
        for ok_key in ok_status.keys():
            divider = uf_status[ok_key] + if_status[ok_key] + ok_status[ok_key]
            score = 0
            if divider > 0:
                score = (ok_status[ok_key] / divider) * 100
            if 'current' in name:
                self.previous_months.append(({ok_key: i['value'], 'score': score}))
            else:
                self.current_months.append(({ok_key: i['value'], 'score': score}))

    def buildActivityByApi(self, part: Any, name) -> None:
        total_count = 0
        for i in part:
            total_count += i['count']

        for i in part:
            for j in i:
                print("jeyakannan--")
                if j in 'count':
                    print((i[j] / total_count) * 100)
                    i[j] = round((i[j] / total_count) * 100, 2)

        self.activity_by_api = part

    def buildCustomerSatisfaction(self, part: Any, name) -> None:
        count = 0
        ok_status = 0
        if_status = 0
        uf_status = 0
        for i in part:
            for j in i['pivot']:
                for k in j:
                    if str(j[k]) in name[0]:
                        ok_status = j['count']
                    if str(j[k]) in name[1]:
                        uf_status = j['count']
                    if str(j[k]) in name[2]:
                        if_status = j['count']
                    self.datas.append(i)
            score = (ok_status / (uf_status + if_status + ok_status)) * 100
            self.customer_satisfaction.append(({i['field']: i['value'], 'score': score}))

    def buildNPSScore(self, part: Any, name) -> None:
        count = 0
        ok_status = 0
        if_status = 0
        uf_status = 0
        for i in part:
            for j in i['pivot']:
                for k in j:
                    if str(j[k]) in name[0]:
                        ok_status = j['count']
                    if str(j[k]) in name[1]:
                        uf_status = j['count']
                    if str(j[k]) in name[2]:
                        if_status = j['count']
                    self.datas.append(i)
            score = round((ok_status / (uf_status + if_status + ok_status)) * 100, 0)
            self.nps_score.append(({i['field']: i['value'], 'score': score}))
            self.customer_satisfaction.append(({i['field']: i['value'], 'score': score}))

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

    def build_availability(self, result, name) -> None:
        return self.builder.produce_availability(result, name)

    def build_response(self, result, name) -> None:
        return self.builder.produce_response(result, name)

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

    def build_customer_experience(self, result, name) -> None:
        return self.builder.produce_customer_experience(result, name)
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
