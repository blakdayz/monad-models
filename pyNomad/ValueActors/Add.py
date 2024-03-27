"""
The Adder actor is a simple actor that binds to functions which return
and object which has an __add__ method. It is used to add objects together
and map the intended result to the call graph.

Example:
```python

"""
from pyNomad.Capsules.Nomad import Nomad

from typing import Generic, Any, Callable
from pyNomad import T, U


from pyNomad.ValueActors.NomadTask import NomadTask


class ChangeState(NomadTask, Generic[T, U]):
    """
    Actor to add two objects together.
    """

    def __init__(self, value: T, func: Callable[[T], Any]) -> None:
        """
        Initialise the actor with the value to add.
        """
        super().__init__(func, value)
        self.value: T = value

    def bind(self, func: Callable[[T], U]) -> "Nomad":
        """
        Bind the actor to a function which will add the value to the result of the function.
        """
        return Nomad(func(self.value))

    def __add__(self, other: Any) -> "Nomad":
        """
        Dunder method to add the value to another object.
        """
        return self.bind(lambda x: x + other)

    def __radd__(self, other: Any) -> "Nomad":
        """
        Dunder method to add the value to another object.
        """
        return self.bind(lambda x: other + x)

    def __iadd__(self, other: Any) -> "Nomad":
        """
        Dunder method to add the value to another object and set the value to the result.

        """
        self.previous_value = self.value  # type: ignore

        def action(value: T):
            """
            Function to add the value to another object to be be bound and tracked
            Returns:

            """
            return lambda x: x + other

        self.value = action(self.value)
        return self.bind(lambda x: x + other)

    def __sub__(self, other: Any) -> "Nomad":
        """
        Dunder method to subtract the value from another object.
        """
        return self.bind(lambda x: x - other)

    def __rsub__(self, other: Any) -> "Nomad":
        """
        Dunder method to subtract the value from another object.
        """
        return self.bind(lambda x: other - x)

    def __isub__(self, other: Any) -> "Nomad":
        """
        Dunder method to subtract the value from another object.
        """
        return self.bind(lambda x: x - other)

    def __mul__(self, other: Any) -> "Nomad":
        """
        Dunder method to multiply the value by another object.
        """
        return self.bind(lambda x: x * other)

    def __rmul__(self, other: Any) -> "Nomad":
        """
        Dunder method to multiply the value by another object.
        """
        return self.bind(lambda x: other * x)

    def __imul__(self, other: Any) -> "Nomad":
        """
        Dunder method to multiply the value by another object.
        """

        return self.bind(lambda x: x * other)

    def __truediv__(self, other: Any) -> "Nomad":
        """
        Dunder method to divide the value by another object.
        """
        return self.bind(lambda x: x / other)
