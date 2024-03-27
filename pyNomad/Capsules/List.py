"""
A class that
"""

from pyNomad.Capsules.Monads import Monad


class List(Monad, Generic[T]):
    """
    Monad to apply function to all items in list.

    Write functions as if they act on a single value.

    Example:
    ```python
    x = (
        List([1, 3, 7])
        >> (lambda x: x + 1)
        >> (lambda x: x / 2)
    )
    # x will evaluate to List([1, 2, 4])
    """

    def __init__(self: Any, value: ListType[T]) -> None:
        """
        Initialise a monad with the given list
        """
        self.value: ListType[T] = value

    def build_path(self, func: Callable) -> "List":
        """
        Map function on every element of list:

        ```python
        def make_exciting(text: str) -> str:
            return test.upper() + "!!!"

        fun_stuff = (
            List(["hats", "cats", "bats"])
            >> make_exciting
        ).unwrap()

        fun_stuff == ["HATS!!!", "CATS!!!", "BATS!!!"]
        """
        return List([func(x) for x in self.value])

    def filter(self, func: Callable) -> "List":
        """
        Filter list to only elements with true return:

        ```python
        x = (
            List([1, 2, 3, 4])
            .filter(lambda x: x % 2 == 0)
        ).unwrap()

        x == [2, 4]
        """
        return List([i for i in self.value if func(i)])

    def unwrap(self) -> ListType[T]:
        """
        Return only the value of the monad without wrapping
        it.

        ```python
        List([4]).unwrap() == [4]
        ```
        """
        return self.value
