from enum import Enum


class InitVar(Enum):
    EMPTY = ""
    UNKNOWN = "unknown"
    MINUS_INT = -1

    @staticmethod
    def get_all():
        """ Returns array containing all values. """
        return [e.value for e in InitVar]