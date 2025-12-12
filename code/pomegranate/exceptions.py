""" Module containing custom exceptions. """


class GenericException(Exception):
    """
    Generic exception class.
    """

    def __init__(self, error_code, error_txt):
        """
        Create a new GenericException.
        """

        self.error_code = error_code
        self.error_txt = error_txt
