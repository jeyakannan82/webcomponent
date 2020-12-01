from __future__ import annotations
from abc import ABC, abstractmethod, abstractproperty
from typing import Any
import pprint


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

    def produce_reliability(self, result) -> None:
        self._customerData.add(result)

    def produce_availability(self, result) -> None:
        self._customerData.add(result)

    def produce_response(self, result) -> None:
        self._customerData.add(result)

    def build_customer_satisfaction(self, result) -> None:
        self._customerData.add(result)

    def build_activity_by_action(self, result) -> None:
        self._customerData.add(result)

    def build_customer_satisfaction(self, result) -> None:
        self._customerData.add(result)

    def build_NPS_score(self, result) -> None:
        self._customerData.add(result)

    def produce_customer_experience(self, result) -> None:
        self._customerData.add(result)

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

    def add(self, part: Any) -> None:
        self.datas.append(part)

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
        """
        The Director works with any builder instance that the client code passes
        to it. This way, the client code may alter the final type of the newly
        assembled product.
        """
        self._builder = builder

    def build_dashboard(self, result) -> None:
        return self.builder.produce_dashboard(result)

    def build_reliability(self, result) -> None:
        return self.builder.produce_reliability(result)

    def build_availability(self, result) -> None:
        return self.builder.produce_availability(result)

    def build_response(self, result) -> None:
        return self.builder.produce_response(result)

    def build_customer_satisfaction(self, result) -> None:
        self.builder.produce_customer_satisfaction(result)

    def build_activity_by_action(self, result) -> None:
        return self.builder.produce_activity_by_action(result)

    def build_customer_satisfaction(self, result) -> None:
        return self.builder.produce_customer_satisfaction(result)

    def build_NPS_score(self, result) -> None:
        return self.builder.produce_NPS_score(result)

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
