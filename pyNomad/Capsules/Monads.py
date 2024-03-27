"""
The base class for all monads.
"""

import logging
from typing import Any, Generic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from pyNomad import T


class Monad(Generic[T]):
    """
    Identity monad (also the parent class for all other monads).

    No additional work is handled on function calls, apart from returning
    a new monad with an updated result.

    Can be used like so:

    ```python
    def make_loud(x:str) -> str:
        return x.upper()

    x = Monad("hello world!") >> make_loud

    print(x.value)
    # prints out "HELLO WORLD!"
    ```
    """

    def __init__(self: Any, value: T) -> "Monad":
        """
        Initialise a monad with the given value
        """
        self.value: T = value

    def build_path(self, func) -> "Monad":
        """
        Establish a "Hunt" via building a path of functions
        which will be executing, passing the result of the previous
        function to the next function in the path after work has been done
        to some value in the path.

        return Monad(func(self.value))
        """

    def __rshift__(self, other) -> "Monad":
        """
        Dunder method to alias bind into >>
        """
        return self.build_path(other)

    def __lshift__(self, other) -> "Monad":
        """
        Dunder method to alias bind into <<
        return self.bind(other). Executes as other(self.value)
        on the right hand side of the operator.
        For alternative syntax:
        ```python
        Monad(2) >> (lambda x: x+1) == x=2 << (lambda x: x+1)
        ```
        """
        return self.build_path(other)

    def unwrap(self) -> T:
        """
        Return only the value of the monad without wrapping
        it.

        ```python
        Monad(4).unwrap() == 4
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


if __name__ == "__main__":
    from pyNomad.Capsules.Results import Encapsulate

    precious_data = Encapsulate(3) >> (lambda x: x + 1) << (lambda x: x + 5)
    print(precious_data)
