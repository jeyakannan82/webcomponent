from __future__ import annotations
from abc import ABC, abstractmethod, abstractproperty
from typing import Any
import pprint


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
    def build_activity_by_action(self, result) -> None:
        pass

    @abstractmethod
    def build_suggestions(self, result) -> None:
        pass


class ConcreteRecommendationBuilder(Builder):

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

    def build_customer_experience_action(self, result) -> None:
        self._customerData.build_customer_experience_action(result)

    def build_transaction_status(self, result) -> None:
        self._customerData.build_transaction_status(result)

    def build_activity_by_action(self, result) -> None:
        self._customerData.build_activity_by_action(result)

    def build_suggestions(self, result) -> None:
        self._customerData.build_suggestions(result)


class CustomerData:

    def __init__(self) -> None:
        self.datas = []
        self.suggestions = []
        self.experience_action = []
        self.transaction_status = []
        self.activity_by_action = []

    def build_customer_experience_action(self, part: Any, name) -> None:
        print('Adding start-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        for i in part:
            for j in i:
                for k in j:
                    print('------')
                    if k in name:
                        print(k)
                        self.experience_action = {name: j[k]}
                        self.datas.append(k)

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


class Director:

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

    def build_activity_by_action(self, result) -> None:
        return self.builder.produce_availability(result)

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
