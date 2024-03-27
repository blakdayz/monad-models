"""
Resilient Nomad Monads- Monad that can recover from errors
Supports async function chaining and call graph generation
with error recovery and alternative strategies, as well as
state signing for value corruption detection and recovery
from errors without having to re-execute the entire call graph,
as well as call graph generation for error recovery and debugging
both in the form of a string and a graphviz graph object at runtime,
as well as a method to generate a graph of the call graph.

Examples:
```python
from pyNomad.Containers.ResilientNomad import CampaignExecutorNomad
from pyNomad.ValueActors.Results import Encapsulate

async def go_to_sleep(x:str) -> str:
    return x.upper()

async def make_pretty(x:str) -> str:
    return x.replace(" ", "_")

async def make_loud_and_pretty_stars(x:str) -> str:
    return f"***{x.upper()}***"


async def make_filtered_quiet(filter:str) -> str:
    return x.replace(filter, "hello?....")

    def PrintSynch(x:str) -> str:
        print(x)

x = CampaignExecutorNomad("hello world!") >>
                                make_loud >>
                                make_pretty >>
                                make_loud_and_pretty_stars >>
                                make_filtered_quiet("hello") <<
                                NomadTask( Encapsulate ) << Monad( PrintSynch ) << make_quiet.bind_task(
                                                                              NomadTask, PrintSynch)
                                >> make_loud

"""
import asyncio
import copy
import hashlib
import logging
from abc import ABCMeta, abstractmethod
from typing import Any, Generic, Optional, Tuple

from pyNomad import T
from pyNomad.Capsules import AsyncNomad
from pyNomad.Capsules.Monads import Monad


class Nomad(Monad, metaclass=ABCMeta):
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

    @abstractmethod
    def sign(self, value):
        """
        Sign the value to ensure that it has not been corrupted

        """
        return hashlib.sha256(str(value).encode()).hexdigest()

    @abstractmethod
    def bind_task(self, func, task):
        pass

    @abstractmethod
    def bind(self, func):
        """
        Bind a asynchronous function to the call graph to execute later.
        """
        pass

    @abstractmethod
    def check(self, value, signature):
        pass

    @abstractmethod
    def __lshift__(self, other):
        pass

    @abstractmethod
    def retry(self, func, alternative):
        """
        Retry a function with an alternative strategy
        :param func: Function being bound to ideal strategy
        :param alternative: Alternative strategy
        """
        pass

    @abstractmethod
    def unwrap(self):
        pass

    @abstractmethod
    def generate_graph(self):
        """
        Generate a graph of the call graph
        """
        pass

    @abstractmethod
    def alternate_bind(self, func, alternative, final):
        """
        Bind function to monad, retrying with alternative if it fails.
        """
        pass


class CampaignExecutorNomad(Nomad, Generic[T]):
    """(formerly Compounds())
    Campaign Executor - Monad that can recover from errors and
    execute a campaign of functions asynchronously
    Supports async function chaining and call graph generation
    with error recovery and alternative strategies, as well as
    state signing for value corruption detection and recovery
    from errors without having to re-execute the entire call graph,

    as well as call graph generation for error recovery and debugging
    both in the form of a string and a graphviz graph object at runtime,
    as well as a method to generate a graph of the call graph.

    Examples:
    ```python
    from pyNomad.Containers.ResilientNomad import CampaignExecutorNomad
    from pyNomad.ValueActors.Results import Encapsulate

    async def make_loud(x:str) -> str:
        return x.upper()

    async def make_pretty(x:str) -> str:
        return x.replace(" ", "_")

    async def make_loud_and_pretty_stars(x:str) -> str:
        return f"***{x.upper()}***"

    async def make_filtered_quiet(filter:str) -> str:
        return x.replace(filter, "hello?....")

        def PrintSynch(x:str) -> str:
            print(x)

    x = CampaignExecutorNomad("hello world!") >>
                                    make_loud >>
                                    make_pretty >>
                                    make_loud_and_pretty_stars >>
                                    make_filtered_quiet("hello") <<
                                    NomadTask( Encapsulate ) << Monad( PrintSynch ) <<
                                    make_quiet.bind_task(NomadTask, PrintSynch)
                                    >> make_loud



    """

    @staticmethod
    def sign(value: T) -> str:
        """
        Sign the value to check for corruption later
        """
        return hashlib.sha256(str(value).encode()).hexdigest()

    async def bind_task(self, func, NomadTask) -> "AsyncNomad":
        """
        Bind a asynchronous function to the call graph to execute later.
        """
        self.call_graph.append(NomadTask)
        try:
            if asyncio.iscoroutinefunction(func):
                self.value = await func(self.value)
            else:
                self.value = func(self.value)
            self.check(self.value, self.signature)  # Check the value
        except ZeroDivisionError as e:
            self.logger.error(f"{e} - {func.__name__}")

            self.value = self.retry(func, lambda x: 0)
        except Exception as e:
            self.error = e
            self.logger.error(f"{e} - {func.__name__}")
        return self

    async def build_path(self, func) -> "Monad":
        """
        Bind a asynchronous function to the call graph to execute later.
        """
        self.call_graph.append(func)  # Update call graph

        compile = compile  # Suppress warning
        try:
            if asyncio.iscoroutinefunction(func):
                self.value = await func(self.value)
            else:
                self.value = func(self.value)
            self.check(self.value, self.signature)  # Check the value
        except ZeroDivisionError as e:
            self.logger.error(f"{e} - {func.__name__}")

            self.value = self.retry(
                func, lambda x: 0
            )  # Retry with alternative strategy
        except Exception as e:
            self.error = e
        return self

    def check(self, value: T, signature: str) -> None:
        assert self.sign(value) == signature, "Value corruption detected"

    def __lshift__(self, other) -> "Monad":
        self.call_graph.append(other)  # Update call graph
        return asyncio.run(self.build_path(other))

    def retry(self, func, alternative) -> "Monad":
        """
        Retry a function with an alternative strategy
        :param func: Function being bound to ideal strategy
        :param alternative: Alternative strategy
        """
        try:
            return self >> func  # Try the original operation
        except Exception as e:
            self.error = e
            return self >> alternative  # If it fails, try the alternative

    def unwrap(self) -> Tuple[T, Optional[Exception], str]:
        return self.value, self.error, str(self.call_graph)

    def generate_graph(self) -> str:
        """
        Generate a graph of the call graph
        """
        graph = "graph TD\n"
        for i, func in enumerate(self.call_graph):
            graph += f"A{i}[{func.__name__}]\n"
            if i > 0:
                graph += f"A{i - 1} --> A{i}\n"
        return graph

    async def alternate_bind(self, func, alternative, final) -> "Monad":
        """
        Bind function to monad, retrying with alternative if it fails.
        """
        try:
            return await self.build_path(func)
        except TypeError as e:  # Catching NoneType exception
            try:
                return await self.retry(func, alternative)
            except Exception as f:
                self.error = f
            finally:
                # If the alternative fails, return the final value
                return await self.build_path(final)
