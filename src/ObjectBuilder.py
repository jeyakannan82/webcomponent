from __future__ import annotations
from abc import ABC, abstractmethod, abstractproperty
from typing import Any
import pprint


class Builder(ABC):
    """
    The Builder interface specifies methods for creating the different parts of
    the Product objects.
    """

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


class ConcreteBuilder(Builder):
    """
    The Concrete Builder classes follow the Builder interface and provide
    specific implementations of the building steps. Your program may have
    several variations of Builders, implemented differently.
    """

    def produce_customer_experience(self) -> None:
        pass

    @property
    def CustomerData(self) -> None:
        pass

    def __init__(self) -> None:
        """
        A fresh builder instance should contain a blank product object, which is
        used in further assembly.
        """
        self._customerData = CustomerData1()
        self.reset()

    def reset(self) -> None:
        pass

    @property
    def customerData(self) -> CustomerData1:
        """
        Concrete Builders are supposed to provide their own methods for
        retrieving results. That's because various types of builders may create
        entirely different products that don't follow the same interface.
        Therefore, such methods cannot be declared in the base Builder interface
        (at least in a statically typed programming language).

        Usually, after returning the end result to the client, a builder
        instance is expected to be ready to start producing another product.
        That's why it's a usual practice to call the reset method at the end of
        the `getProduct` method body. However, this behavior is not mandatory,
        and you can make your builders wait for an explicit reset call from the
        client code before disposing of the previous result.
        """
        customer_data = self._customerData
        self.reset()
        return customer_data

    def produce_dashboard(self, result) -> None:
        self._customerData.add(result)

    def produce_customer_experience(self, result) -> None:
        self._customerData.add(result)

    def produce_solutions_object(self, result) -> None:
        self._customerData.add(result)


class CustomerData1:
    """
    It makes sense to use the Builder pattern only when your products are quite
    complex and require extensive configuration.

    Unlike in other creational patterns, different concrete builders can produce
    unrelated products. In other words, results of various builders may not
    always follow the same interface.
    """

    def __init__(self) -> None:
        self.datas = []

    def add(self, part: Any) -> None:
        self.datas.append(part)

    def list_data(self) -> None:
        # print(f"Product parts: {', '.join(self.datas)}", end="")
        print("Number of hits: {0}".format(len(self.datas)))
        for i in self.datas:
            pprint.pprint(i)


class Director:
    """
    The Director is only responsible for executing the building steps in a
    particular sequence. It is helpful when producing products according to a
    specific order or configuration. Strictly speaking, the Director class is
    optional, since the client can control builders directly.
    """

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

    """
    The Director can construct several product variations using the same
    building steps.
    """

    def build_dashboard(self, result) -> None:
        self.builder.produce_dashboard(result)

    def build_solutions(self, result) -> None:
        self.builder.produce_solutions_object(result)

    def build_customer_experience(self, result) -> None:
        self.builder.produce_customer_experience(result)
        # self.builder.produce_part_b()
        # self.builder.produce_part_c()


if __name__ == "__main__":
    """
    The client code creates a builder object, passes it to the director and then
    initiates the construction process. The end result is retrieved from the
    builder object.
    """

    director = Director()
    builder = ConcreteBuilder()
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