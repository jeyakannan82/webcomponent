from __future__ import annotations
from abc import ABC, abstractmethod, abstractproperty
from typing import Any
from copy import deepcopy
import pprint


class Builder(ABC):

    @abstractproperty
    def CustomerData(self) -> None:
        pass

    @abstractmethod
    def build_transaction_details(self, result,name) -> None:
        pass

    @abstractmethod
    def build_availability(self, result,name) -> None:
        pass

    @abstractmethod
    def build_produce_success(self, result,name) -> None:
        pass

    @abstractmethod
    def build_produce_uptime(self, result,name) -> None:
        pass

    @abstractmethod
    def build_produce_category(self, result,name) -> None:
        pass

    @abstractmethod
    def build_transaction_by_api(self, result,name) -> None:
        pass

    @abstractmethod
    def build_good_experience(self, result,name) -> None:
        pass

    @abstractmethod
    def build_average_experience(self, result,name) -> None:
        pass

    @abstractmethod
    def build_bad_experience(self, result,name) -> None:
        pass

    @abstractmethod
    def build_customer_experience(self, result,name) -> None:
        pass


class ConcreteExperienceBuilder(Builder):

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

    def build_customer_experience(self, result,name) -> None:
        self._customerData.add(result,name)

    def build_produce_success(self, result, name) -> None:
        self._customerData.buildSuccessRate(result, name)

    def build_produce_uptime(self, result, name) -> None:
        self._customerData.buildUpTime(result, name)

    def build_produce_category(self, result, name) -> None:
        self._customerData.buildCategory(result, name)

    def build_bad_experience(self, result ,name) -> None:
        self._customerData.buildBadExperience(result ,name)

    def build_average_experience(self, result ,name) -> None:
        self._customerData.buildAverageExperience(result ,name)

    def build_good_experience(self, result ,name) -> None:
        self._customerData.buildGoodExperience(result ,name)

    def build_transaction_by_api(self, result ,name) -> None:
        self._customerData.build_transaction_by_api(result ,name)

    def build_availability(self, result,name) -> None:
        self._customerData.build_availability(result,name)

    def build_transaction_details(self, result,name) -> None:
        self._customerData.build_availability(result,name)


class CustomerData:

    def __init__(self) -> None:
        self.datas = []
        self.transaction_details = []
        self.availability = []
        self.transaction_by_api = []
        self.good_experience = []
        self.average_experience = []
        self.bad_experience = []
        self.successRate = []
        self.uptime = []
        self.category = []

    def getSuccessData(self):
        return self.successRate

    def getUptimeData(self):
        return self.uptime

    def getCategoryData(self):
        return self.category

    def getGoodExperience(self):
        return self.good_experience

    def getAverageExperience(self):
        return self.average_experience

    def getBadExperience(self):
        return self.bad_experience

    def buildSuccessRate(self, part: Any, name) -> None:
        print('buildSuccessRate-----')
        total_request = 0
        ok_status = 0
        if_status = 0
        uf_status = 0
        success_transaction = []
        print(part)
        for i in part:
            for j in i:
                if str(i[j]) in 'OK':
                    ok_status = i['count']
                if str(i[j]) in 'UF':
                    uf_status = i['count']
                if str(i[j]) in 'IF':
                    if_status = i['count']
        total_request = ok_status + uf_status + if_status
        self.successRate = [{'y': round((ok_status / total_request) * 100, 0), 'label': 'Success'},
                                 {'y': round((uf_status / total_request) * 100, 0), 'label': 'User Failures'},
                                 {'y': round((if_status / total_request) * 100, 0), 'label': 'Server Error'}]

    def buildUpTime(self, part: Any, name) -> None:
        print('buildUpTime-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        for i in part:
            for j in i:
                if j in name:
                    self.uptime.append(deepcopy(i))
                    self.datas.append(deepcopy(i))

    def buildCategory(self, part: Any, name) -> None:
        print('buildCategory-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        results = part['facet_counts']['facet_pivot']['type']
        total_count = part['response']['numFound']
        for i in results:
            self.category.append(({'label': i['value'], 'y': round(i['count']/total_count, 2)}))

    def buildBadExperience(self, part: Any, name) -> None:
        print('buildBadExperience-----')
        # print(f"Product parts: {', '.join(part)}", end="")

        total = len(part)
        count = 0
        ok_status = 0
        if_status = 0
        uf_status = 0
        user_exp_percent = 0
        percentage = ''
        meet = ''
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
            user_exp_percent = round((ok_status / (uf_status + if_status + ok_status)) * 100, 0)
            if  user_exp_percent < 60:
                meet = 'No'
                percentage = str(user_exp_percent) + '%'
            else:
                meet = 'No'
                percentage = str(user_exp_percent) + '%'

            if user_exp_percent < 60:
                self.bad_experience.append(({i['field']: i['value'], 'success': ok_status, 'user_failed': uf_status,
                                              'server_failed': if_status, 'percentage': percentage, 'meet': meet}))

    def buildAverageExperience(self, part: Any, name) -> None:
        print('buildAverageExperience-----')
        # print(f"Product parts: {', '.join(part)}", end="")

        total = len(part)
        count = 0
        ok_status = 0
        if_status = 0
        uf_status = 0
        user_exp_percent = 0
        percentage = ''
        meet = ''
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

            user_exp_percent = round((ok_status / (uf_status + if_status + ok_status)) * 100, 0)
            if  70 > user_exp_percent > 60:
                meet = 'No'
                percentage = str(user_exp_percent) + '%'

            if 70 > user_exp_percent > 60:
                self.average_experience.append(({i['field']: i['value'], 'success': ok_status, 'user_failed': uf_status,'server_failed': if_status, 'percentage': percentage, 'meet': meet}))

    def buildGoodExperience(self, part: Any, name) -> None:
        print('buildGoodExperience-----')
        # print(f"Product parts: {', '.join(part)}", end="")

        total = len(part)
        count = 0
        ok_status = 0
        if_status = 0
        uf_status = 0
        user_exp_percent = 0
        percentage = ''
        meet =''
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
            user_exp_percent = round((ok_status / (uf_status + if_status + ok_status)) * 100, 0)
            if user_exp_percent > 70.0:
               meet = 'Yes'
               percentage = str(user_exp_percent) +'%'
            else:
               meet ='No'
               percentage = str(user_exp_percent) + '%'

            if user_exp_percent > 70:
               self.good_experience.append(({i['field']: i['value'], 'success': ok_status, 'user_failed':uf_status, 'server_failed':if_status,'percentage':percentage, 'meet':meet }))

    def build_transaction_by_api(self, part: Any, name) -> None:
        print('Adding start-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        for i in part:
            if i in name:
                if i in name:
                    print(i)
                    self.transaction_by_api.append(({i: part[i]}))
                    self.datas.append(i)

    def build_availability(self, part: Any, name) -> None:
        print('Adding start-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        for i in part:
            if i in name:
                print(i)
                if i in name:
                    self.availability.append(({i: part[i]}))
                    self.datas.append(i)

    def build_transaction_details(self, part: Any, name) -> None:
        print('Adding start-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        for i in part:
            if i in name:
                print(i)
                if i in name:
                    self.transaction_details.append(({i: part[i]}))
                    self.datas.append(i)

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


class ExperienceDirector:

    def __init__(self) -> None:
        self._builder = None

    @property
    def builder(self) -> Builder:
        return self._builder

    @builder.setter
    def builder(self, builder: Builder) -> None:

        self._builder = builder

    def build_transaction_details(self, result,name) -> None:
        return self.builder.produce_dashboard(result,name)

    def build_availability(self, result,name) -> None:
        return self.builder.produce_availability(result,name)

    def build_success_rate(self, result,name) -> None:
        return self.builder.build_produce_success(result,name)

    def build_uptime(self, result,name) -> None:
        return self.builder.build_produce_uptime(result,name)

    def build_category(self, result,name) -> None:
        return self.builder.build_produce_category(result,name)

    def build_transaction_by_api(self, result,name) -> None:
        return self.builder.produce_response(result,name)

    def build_good_experience(self, result,name) -> None:
        self.builder.build_good_experience(result,name)

    def build_average_experience(self, result,name) -> None:
        return self.builder.build_average_experience(result,name)

    def build_bad_experience(self, result,name) -> None:
        return self.builder.build_bad_experience(result,name)

    def build_customer_experience(self, result,name) -> None:
        return self.builder.produce_customer_experience(result,name)
        # self.builder.produce_part_b()
        # self.builder.produce_part_c()


if __name__ == "__main__":

    director = ExperienceDirector()
    builder = ConcreteExperienceBuilder()
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
