"""
A play on the word monad, nomad is a container for a value that can be passed around and manipulated safely.
"""

import asyncio
from abc import ABC
from typing import TypeVar, Generic, Optional, Tuple

from pyNomad import T
from pyNomad import Capsules
from pyNomad.ValueActors import NomadTask

from pyNomad.Capsules.Monads import Monad
from pyNomad.Capsules.Nomad import Nomad


class AsyncNomad(Nomad, Generic[T], ABC):
    """
    Monad to handle async functions.

    Example:
    ```python
    async def make_loud(x:str) -> str:
        return x.upper()

    x = AsyncMonad("hello world!") >> make_loud

    print(x.value)
    # prints out "HELLO WORLD!"
    ```
    """

    async def build_path(self, func) -> "Nomad":
        """
        Method to apply async function to value of Monad.
        Returns a monad with the updated value.

        Example:
        ```python
        AsyncMonad(2).bind(lambda x: x+1) == AsyncMonad(3)
        ```

        Can be aliased with `>>` symbol:
        ```python
        (AsyncMonad(2) >> (lambda x: x+1)) == AsyncMonad(3)
        ```
        """
        return Nomad(await func(self.value))

    def __rshift__(self, other) -> "Nomad":
        """
        Dunder method to alias bind into >>
        """
        return self.build_path(other)

    def __lshift__(self, other) -> "NomadTask":
        """
        Method to bind a task of asynchronous Monad meaning that it can be used to chain functions together without
          executing them. They will be executed when the monad is unwrapped, and those functions will be executed
          asynchronously with the asyncio library. The right shift chains normal functions together, but the left shift


          ```python
          AsyncMonad(2) >> (lambda x: x+1) << (lambda x: x+2)
          ```

          In CompoundMonad, this will be used to add a function
          to the call graph without executing it. It will be
          executed when the monad is unwrapped.

        """
        return self.build_path(other)

    def unwrap(self) -> T:
        """
        Return only the value of the monad without wrapping
        it.

        ```python
        AsyncMonad(4).unwrap() == 4
        ```
        """
        return self.value

    def __str__(self) -> str:
        """
        String representation
        """
        return f"{self.__class__.__name__}({self.value})"

    def __repr__(self) -> str:
        """
        For repls
        """
        return self.__str__()

    def __eq__(self, other) -> bool:
        """
        Equality
        """
        return self.value == other.value

    def __ne__(self, other) -> bool:
        """
        Inequality
        """
        return self.value != other.value

    def __lt__(self, other) -> bool:
        """
        Less than
        """
        return self.value < other.value

    def __gt__(self, other) -> bool:
        """
        Greater than
        """
        return self.value > other.value

    def __le__(self, other) -> bool:
        """
        Less than or equal to
        """
        return self.value <= other.value
