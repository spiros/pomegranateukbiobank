""" Module containing error codes. """

from enum import Enum
from enum import auto


class ErrorCode(Enum):
    """
    Generic error class.
    """

    DB_CONNECTION_FAILED = auto()
    NO_ACTION_SPECIFIED = auto()
    PHENOTYPE_NOT_FOUND = auto()
