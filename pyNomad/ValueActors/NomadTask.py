"""
Nomad Task Monad - A form of an actor nomad function that takes a function and a value and returns a
        function that takes no arguments and returns the result of the original
        function applied to the value.
"""
from typing import Any, Callable, Generic
from pyNomad import T
from pyNomad.Capsules import Nomad, Results


class NomadTask(Generic[T], Callable[[Callable[[T], Any], T], Any]):
    """
    A NomadTask is a function that takes a function and a value and returns a
        function that takes no arguments and returns the result of the original
        function applied to the value.

        Example:
        ```python
        def make_loud(x:str) -> str:
            return x.upper()

        x = Monad("hello world!") >> task(make_loud)

        print(x.value)
        # prints out "HELLO WORLD!"
        ```

        The task is useful for creating a call graph of functions that can be
        executed later.
    """

    def __init__(self, func: Callable[[T], Any], value: T) -> None:
        self.func = func
        self.value = value

    async def __call__(self, *args, **kwargs) -> Any:
        return await self.func(self.value)

    def __repr__(self) -> str:
        return f"task({self.func.__name__}, {self.value})"

    def __str__(self) -> str:
        return f"task({self.func.__name__}, {self.value})"

    def __eq__(self, other) -> bool:
        return self.func == other.func and self.value == other.value

    def __add__(self, other: Any) -> "Nomad":
        """
        Dunder method to add the value to another object.
        """
        return (
            Nomad(lambda x: x + other) << self.func(self.value) >> Results
        )  # all nomads are monads but not all monads are nomads
