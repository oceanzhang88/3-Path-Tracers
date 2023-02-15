import logging
from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")
logger = logging.getLogger(__name__)


class Registry(Generic[T]):
    """OOP factory magic"""

    def __init__(self, name: str, base: Callable[..., T]) -> None:
        self.name = name
        self.constructors: dict[str, Callable[..., T]] = {}

    def add(self, name: str, constructor: Callable[..., T]) -> None:
        logger.info(f"Register {self.name}: {name}")
        self.constructors[name] = constructor

    def get(self, name: str) -> Callable[..., T]:
        return self.constructors[name]

    def build(self, name: str, kwargs: dict[str, Any]) -> T:
        return self.get(name)(**kwargs)
