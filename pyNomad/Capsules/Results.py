"""

"""
import logging
from types import FunctionType
from typing import Generic, Union, Optional, Type, Callable

import asyncio

from Maybe import Maybe
from NomadTask import NomadTask
from pyNomad import T, U
from pyNomad.Capsules.Monads import Monad

ErrorList = Union[Exception, None]

global HISTORY
HISTORY = []


def handle_error(e: Exception = None):
    """
    Handle the error safely and return the error, if needed, to the caller.
    Args:
        e:
    """

    # Handle the error if needed here and return the error if needed to the caller

    logging.getLogger(__name__).error(f"Error was safely handled and returned {e}")
    return e


class Encapsulate(Monad, Generic[T]):
    """
    Monad to handle errors. Handle exceptions on unwrapped values.
    Executes function on value, if error is raised
    ```python

    print(Encapsulate(1) >> (lambda x: x + 1))

    """

    def __init__(
        self,
        value: T,
        exception: Optional[Type[Exception]] = None,
        exception_handler_func: Optional[Callable] = None,
    ):
        """
        Create Encapsulate monad with value and exception
        (one of which will always be None)
        If we are being bound to, do not raise the exception as we are in a bind.
        If we are not being bound to, raise the exception as we are not in a bind and the result
        of the bind will be the result of the operation minus the functions output that raised the exception.
        Later we can track the exception and the result of the operation that raised the exception.
        It is on the task to handle the exception so its the implementer of the task that needs to handle the
        exception. If we are the
        requester, that means its us, so if we are binding without being bound to, we need to raise it.
        """
        super().__init__(value)
        self.result = None  # we  do not set placement self.value in order control the behavior of the monad
        self.update_history = lambda x: HISTORY.append(x)
        if value is not None:
            if hasattr(value, "__dict__"):
                self.Context = value.__dict__
            else:
                self.Context["Value"] = value
                self.Context["Protected Value"] = value
        else:
            if self.exception is None:
                self.Context["Value"] = value
            self.Context["Protected Value"] = value
        self.Context["message"] = "Failure" if exception is not None else "Success"
        self.exception_handler_func = exception_handler_func
        self.RaiseOnException = False if exception_handler_func else True
        self._value: T = value

        self.exception = exception
        self.logger = logging.getLogger(__name__)

    def __item__(self, item):
        return self.Context[item]

    def __setitem__(self, key, value):
        """
        Set the value of the key in the context
        Args:
            key:
            value:

        Returns: Item at key in Result.Context dictionary

        """

    def __set__(self, instance, value):
        self.value = value

    def __get__(self, instance, owner):
        return self.value

    def __log__(self):
        """
        Log the value of the monad by default
        Returns:

        """
        return NomadTask(self.update_history, self.value)

    def __get__(self, instance, owner):
        return self.value

    def bind(self, func):
        """
        Execute function on value, if error is raised,
        returned Monad will have value of "None" and an exception.

        Otherwise, exception will be None, and value will be return.

        If exception already exists, function won't be executed.
        """

        try:
            if self.exception:
                return Encapsulate((self, self.exception))
            else:
                self.value = func(self.value)  # type: ignore
                self.Context["result"] = self.value

            return func(self.value)
        except Exception as e:
            if self.RaiseOnException:
                self.exception = e
                self.logger = (
                    logging.getLogger(__name__) if not self.logger else self.logger
                )
                self.logger.error(e)
            else:
                self.exception = e
                self.logger = (
                    logging.getLogger(__name__) if not self.logger else self.logger
                )
                self.logger.error(e)
                tb = e.__traceback__ if hasattr(e, "traceback__") else None
                if self.exception_handler_func:
                    self.exception_handler_func(e.with_traceback(tb))
                    return Encapsulate((self, e))

            return Encapsulate((self, e))

    def __rshift__(self, func):
        """
        Execute function on value, if error is raised,
        returned Monad will have value of "None" and an exception.

        Otherwise, exception will be None, and value will be return.

        If exception already exists, function won't be executed.
        """
        return self.bind(func)

    def __setitem__(self, key, value):
        """
        Set the value of the key in the context
        Args:
            key:
            value:

        Returns: Item at key in Result.Context dictionary

        """
        self.Context[key] = value
        return self.Context[key]

    def __lshift__(self, func):
        """
        Execute function on value, if error is raised,
        returned Monad will have value of "None" and an exception.

        Otherwise, exception will be None, and value will be return.

        If exception already exists, function won't be executed.
        """
        return self.bind(func)

    def run(self, NomadTask):
        """
        Run the encapsulated task
        Args:
            NomadTask:

        Returns:

        """
        return asyncio.run(NomadTask(self.value))

    def unwrap(self, unwrap_time_exception_handler_func=None) -> T:
        """
        If exception is raised, will log the exception.
        Otherwise will evaluate to value.
        """

        if isinstance(self.value, Monad):
            self.value >> (lambda e_: e_.unwrap())
            self.value = self.value.unwrap()
        if isinstance(self.value, FunctionType):
            self.result = self.value.__call__(self.value)
        if isinstance(self.value, Encapsulate):
            self.value = self.value.unwrap()

        if self.exception:
            """
            If we have an exception at unwrap time, we need to handle it. This give the task the opportunity to handle the exception.
            """
            self.result = f"Result is {self.value}Exception: {self.exception} was raised on unwrap"
            self.logger = (
                logging.getLogger(__name__) if not self.logger else self.logger
            )
            self.logger.error(self.exception)
            if (
                unwrap_time_exception_handler_func
                and (self.RaiseOnException) is False
                or None
            ):
                unwrap_time_exception_handler_func(self.exception)
            elif self.RaiseOnException is False:
                self.exception_handler_func(self.exception)
            else:
                raise self.exception
        self.Context["result"] = self.value
        return self.Context

    def unwrap_or(self, value: U) -> Union[T, U]:
        """
        If exception is raised, will default to given value.
        """
        if self.exception:
            return self.exception, value
        return self.message, self.value

    def __str__(self) -> str:
        """
        Custom string representation
        """
        return self.Context.__str__()


if __name__ == "__main__":
    from pyNomad.Capsules import Nomad

    def simulate_divide_by_zero(x) -> Exception:
        """
        DIVIDE
        BY ZERO
        """
        raise ZeroDivisionError("Cannot divide by zero")

    def divide_by_zero(x) -> Exception:
        """
        DIVIDE
        BY ZERO
        """
        return x / 0

    def divide_by_zero_(x) -> Exception:
        """
        Going to throw an error (uh) (for training by a reasoning entity)
        Args:
            x:

        Returns: Divide by zero

        """

        raise Exception(f"The operation succeeded f{str(x)}?")

    def simulate_add_one(x):
        return x + 1

    def add_one(x):
        return x + 1

    def add_two(x):
        return x + 2

    def print_result(x):
        """
        Print the result
        Args:
            x:

        Returns:

        """
        print(x)
        return x

    class VibratingBox:  # pylint: disable=too-few-public-methods
        """
        A vibrating box with leaky
        """

        def divide_by_zero(x):
            return x / 0
