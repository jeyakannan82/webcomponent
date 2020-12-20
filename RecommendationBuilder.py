from __future__ import annotations
from abc import ABC, abstractmethod, abstractproperty
from typing import Any

import numpy as np
import pandas as pd
import pprint
import json
from pandas.io.json import json_normalize


class Builder(ABC):

    @abstractproperty
    def CustomerData(self) -> None:
        pass

    @abstractmethod
    def build_customer_experience_action(self, result) -> None:
        pass

    @abstractmethod
    def build_transaction_status(self, result) -> None:
        pass

    @abstractmethod
    def build_Radar_data(self, result, name) -> None:
        pass

    @abstractmethod
    def build_suggestions(self, result) -> None:
        pass


class ConcreteRecommendationBuilder(Builder):

    def build_customer_experience_action(self, result) -> None:
        pass

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

    def build_transaction_status(self, result) -> None:
        self._customerData.build_transaction_status(result)

    def build_Radar_data(self, result, name) -> None:
        self._customerData.build_Radar_data(result, name)

    def build_suggestions(self, result) -> None:
        self._customerData.build_suggestions(result)


class CustomerData:

    def __init__(self) -> None:
        self.datas = []
        self.suggestions = {}
        self.experience_action = []
        self.transaction_status = []
        self.activity_by_action = []
        self.radar_data = []
        self.caption = {}
        self.error_count = {}
        self.error_codes = []
        self.colors = {'400': '#DFFF00-Bad Request', '401': '#FFBF00-Unauthorized', '403': '#FF7F50-Forbidden',
                       '404': '#DE3163-Not Found', '405': '#9FE2BF-Method Not Allowed', '409': "#6FE1BF-Conflict",
                       '412': '#255818-Precondition Failed', '429': '#581845-Too Many Requests',
                       '502': '#1FC723-Bad Gateway', '406': '#40E0D0-Not Acceptable', '408': '#6495ED-Request Timeout',
                       '415': '#CCCCFF-Unsupported Media Type',
                       '500': '#800080-Internal Server Error',
                       '501': '#808000-Not Implemented', '503': '#000080-Service Unavailable',
                       '504': '#00FF00-Gateway Timed out', '201': '#C0C0C0-Created', '200': '#FA8072-Success'}

    def getCaption(self):
        return self.caption

    def getErrorCodes(self):
        for error_objects in self.error_count:
            for error_code in self.error_count[error_objects]:
                color_array = self.colors.get(str(error_objects)).split("-")
                self.error_codes.append(({'y': self.error_count[error_objects][str(error_code)], 'label': color_array[1]}))
        return self.error_codes

    def getRadarData(self):
        caption = {}
        data = {}

        for services in self.suggestions:
            for service_code in self.suggestions[services]:
                color_array = self.colors.get(str(service_code)).split("-")
                self.caption[service_code] = color_array[1]
            self.radar_data.append({'data': self.suggestions[services], 'meta': {'color': color_array[0]}})

        return self.radar_data

    def build_Radar_data(self, part: Any, name) -> None:
        print('build_Radar_data-----')
        count = 0
        ok_status = 0
        if_status = 0
        uf_status = 0
        other_status = 0

        print("Total count----")
        for i in part['facet_counts']['facet_pivot']['type,response_code']:
            total_count = i['count']
            for j in i['pivot']:
                data_array = []
                for k in j:
                    if str(j['value']) not in "200":
                        if k in 'value':
                            if j[k] in self.error_count.keys():
                                count = self.error_count.get(j[k])[str(j[k])] + j['count']
                                self.error_count.get(str(j[k])).update({str(j[k]): count})
                            else:
                                count = j['count']
                            self.error_count[str(j[k])] = {str(j['value']): count}
                    if str(j['value']) not in "200":
                        score = round((j['count'] / total_count)*10, 2)
                        if i['value'] in self.suggestions.keys():
                            data_array.append(self.suggestions[i['value']])
                            data_array.append(({j['value']: score}))
                            self.suggestions.get(i['value']).update({str(j['value']): score})
                        else:
                            data_array.append(({j['value']: score}))
                            self.suggestions[i['value']] = {str(j['value']): score}

    def build_transaction_status(self, part: Any, name) -> None:
        print('Adding start-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        for i in part:
            for j in i:
                for k in j:
                    print('------')
                    if k in name:
                        print(k)
                        self.transaction_status = {name: j[k]}
                        self.datas.append(k)

    def build_activity_by_action(self, part: Any, name) -> None:
        print('Adding start-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        for i in part:
            for j in i:
                for k in j:
                    print('------')
                    if k in name:
                        print(k)
                        self.activity_by_action = {name: j[k]}
                        self.datas.append(k)
                        ''' def weighted_rating(x, m=m, C=C):
        v = x['vote_count']
        R = x['vote_average']
        # Calculation based on the IMDB formula
        return (v / (v + m) * R) + (m / (m + v) * C)'''

    def build_suggestions(self, part: Any, name) -> None:
        print('Adding start-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        for i in part:
            for j in i:
                for k in j:
                    print('------')
                    if k in name:
                        print(k)
                        self.suggestions = {name: j[k]}
                        self.datas.append(k)

    def list_data(self) -> None:
        # print(f"Product parts: {', '.join(self.datas)}", end="")
        print("Number of hits: {0}".format(len(self.datas)))
        for i in self.datas:
            pprint.pprint(i)

    def populate_data(self) -> None:
        # print(f"Product parts: {', '.join(self.datas)}", end="")
        print("Number of hits: {0}".format(len(self.datas)))
        for i in self.datas:
            pprint.pprint(i)


class RecommendationDirector:

    def __init__(self) -> None:
        self._builder = None

    @property
    def builder(self) -> Builder:
        return self._builder

    @builder.setter
    def builder(self, builder: Builder) -> None:
        self._builder = builder

    def build_suggestions(self, result) -> None:
        return self.builder.produce_dashboard(result)

    def build_Radar_data(self, result, name) -> None:
        return self.builder.build_Radar_data(result, name)

    def build_transaction_status(self, result) -> None:
        return self.builder.produce_response(result)

    def build_customer_experience_action(self, result) -> None:
        self.builder.produce_customer_satisfaction(result)


if __name__ == "__main__":
    director = Director()
    builder = ConcreteRecommendationBuilder()
    director.builder = builder

    print("Standard basic product: ")
    director.build_suggestions()
    builder.customerData.list_data()

    print("\n")

    print("Standard full featured product: ")
    director.build_activity_by_action()
    builder.customerData.list_data()

    print("\n")

    print("Custom product: ")
    builder.build_transaction_status()
    builder.produce_solutions_object()
