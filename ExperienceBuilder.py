from __future__ import annotations
from abc import ABC, abstractmethod, abstractproperty
from typing import Any
import pprint


class Builder(ABC):

    @abstractproperty
    def CustomerData(self) -> None:
        pass

    @abstractmethod
    def build_transaction_details(self, result) -> None:
        pass

    @abstractmethod
    def build_availability(self, result) -> None:
        pass

    @abstractmethod
    def build_transaction_by_api(self, result) -> None:
        pass

    @abstractmethod
    def build_good_experience(self, result) -> None:
        pass

    @abstractmethod
    def build_average_experience(self, result) -> None:
        pass

    @abstractmethod
    def build_bad_experience(self, result) -> None:
        pass

    @abstractmethod
    def build_customer_experience(self, result) -> None:
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

    def build_customer_experience(self, result) -> None:
        self._customerData.add(result)

    def build_bad_experience(self, result) -> None:
        self._customerData.build_customer_experience(result)

    def build_average_experience(self, result) -> None:
        self._customerData.add(result)

    def build_good_experience(self, result) -> None:
        self._customerData.build_average_experience(result)

    def build_transaction_by_api(self, result) -> None:
        self._customerData.build_transaction_by_api(result)

    def build_availability(self, result) -> None:
        self._customerData.build_availability(result)

    def build_transaction_details(self, result) -> None:
        self._customerData.build_availability(result)


class CustomerData:

    def __init__(self) -> None:
        self.datas = []
        self.transaction_details = []
        self.availability = []
        self.transaction_by_api = []
        self.good_experience = []
        self.average_experience = []
        self.bad_experience = []

    def build_bad_experience(self, part: Any, name) -> None:
        print('Adding start-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        for i in part:
            if i in name:
                print(i)
                if i in name:
                    print(i)
                    self.bad_experience.append(({i: part[i]}))
                    self.datas.append(i)

    def build_average_experience(self, part: Any, name) -> None:
        print('Adding start-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        for i in part:
            if i in name:
                print(i)
                if i in name:
                    print(i)
                    self.average_experience.append(({i: part[i]}))
                    self.datas.append(i)

    def build_good_experience(self, part: Any, name) -> None:
        print('Adding start-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        for i in part:
            if i in name:
                print(i)
                if i in name:
                    print(i)
                    self.good_experience.append(({i: part[i]}))
                    self.datas.append(i)

    def build_transaction_by_api(self, part: Any, name) -> None:
        print('Adding start-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        for i in part:
            if i in name:
                print(i)
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
                    print(i)
                    self.availability.append(({i: part[i]}))
                    self.datas.append(i)

    def build_transaction_details(self, part: Any, name) -> None:
        print('Adding start-----')
        # print(f"Product parts: {', '.join(part)}", end="")
        for i in part:
            if i in name:
                print(i)
                if i in name:
                    print(i)
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


class Director:

    def __init__(self) -> None:
        self._builder = None

    @property
    def builder(self) -> Builder:
        return self._builder

    @builder.setter
    def builder(self, builder: Builder) -> None:

        self._builder = builder

    def build_transaction_details(self, result) -> None:
        return self.builder.produce_dashboard(result)

    def build_availability(self, result) -> None:
        return self.builder.produce_availability(result)

    def build_transaction_by_api(self, result) -> None:
        return self.builder.produce_response(result)

    def build_good_experience(self, result) -> None:
        self.builder.produce_customer_satisfaction(result)

    def build_average_experience(self, result) -> None:
        return self.builder.produce_activity_by_action(result)

    def build_bad_experience(self, result) -> None:
        return self.builder.produce_customer_satisfaction(result)

    def build_customer_experience(self, result) -> None:
        return self.builder.produce_customer_experience(result)
        # self.builder.produce_part_b()
        # self.builder.produce_part_c()


if __name__ == "__main__":

    director = Director()
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
