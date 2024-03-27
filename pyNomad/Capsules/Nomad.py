"""
Nomad is a monad that can be used to chain functions together without
executing them. They will be executed when the monad is unwrapped.

This is useful for creating a call graph of functions that can be.
Nomads "Hunt" first and "Gather" later.
Hunting is the process of binding functions to the call graph, and establishing
a strategy for executing them. Gathering is the process of executing the call
graph according to the strategy.

Gather Monads are the left shift operator, <<, and the gather method itself.
Hunt monads are the right shift operator, >>, and the hunt method itself.


"""
import copy
import logging
from abc import ABCMeta, abstractmethod
from typing import Any
from hashlib import sha256

from pyNomad import T
from pyNomad.Capsules.Monads import Monad


class Nomad(Monad, metaclass=ABCMeta):
    """ """

    def __init__(self: Any, value: T) -> None:
        """
        Initialise a monad with the given value. This is a compound monad
        meaning that it can be used to chain functions together without
        executing them. They will be executed when the monad is unwrapped.

        This is useful for creating a call graph of functions that can be
        executed later. This is useful for creating a call graph of functions
        in the case of an error, where you want to know what functions were
        executed before the error occurred and in what order so that you can
        recover from the error precisely without having to re-execute the
        entire call graph.
        A retry function is also provided to allow for alternative strategies

        """
        super().__init__(value)
        self.call_graph = []  # Initialize call graph
        self.error = None
        self.signature = self.sign(value)
        self.value = copy.deepcopy(value)
        self.logger = logging.getLogger(__name__)
        self.task = None

    @abstractmethod
    def sign(self, value: T) -> str:
        """
        Sign the value to ensure that it has not been corrupted

        :value: The value to be signed
        :return: The signature of the value
        """
        return sha256(str(value).encode()).hexdigest()

    @abstractmethod
    def assign_task(self, NomadTask) -> "Nomad":
        """
        Assign a task to the nomad
        The task is a NomadTask, which
        is a function that takes a function and a value and returns a
        function that takes no arguments and returns the result of the original
        function applied to the value.

        Example:
        ```python
        def make_loud(x:str) -> str:
            return x.upper()


        def make_pretty(x:str) -> str:
            return x.replace(" ", "_")

        def make_loud_and_pretty_stars(x:str) -> str:
            return f"***{x.upper()}***"

        def make_filtered_quiet(filter:str) -> str:
            return x.replace(filter, "hello?....")

        x = Monad("hello world!").assign_task(NomadTask,
                                        make_loud) >>
                                        make_pretty >>
                                        make_loud_and_pretty_stars >>
                                        make_filtered_quiet("hello")
        x.value
        # prints out "***HELLO?...._WORLD!***"

        ```
        """
        self.task = NomadTask
        return self

    @abstractmethod
    def build_path(self, func):
        """
        Bind an asynchronous function to the call graph to execute later.
        """
        pass

    @abstractmethod
    def validate(self, value_bytes: bytearray, signature: str) -> bool:
        """
        Validates the byte_arrays signature to ensure that it has not been corrupted
        """
        self.logger.debug(
            f"Checking signature of {value_bytes} with signature {signature}"
        )
        return self.sign(value_bytes) == signature

    @abstractmethod
    def __lshift__(self, other):
        """
        Dunder method to alias bind into << for alternative syntax:

        ```python

        Monad(2) >> (lambda x: x+1) == x=2 << (lambda x: x+1)
        Monad(2) >> (lambda x: x+1) == Monad(2).bind(lambda x: x+1)

        x = Monad(2) >> (lambda x: x+1) >> (lambda x: x+1) >> (lambda x: x+1)
        x.value == 5

        ```
        """
        return self.bind(other)

    def bind(self, other):
        """
        Bind a function to the call graph to execute later.
        """
        self.build_path(other)
        return self
