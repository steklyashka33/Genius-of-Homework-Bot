from typing import Self


class Singleton:
    _instance = None
    def __new__(cls, *args, **kwargs) -> Self:
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance