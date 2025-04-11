from apifuzzer.__init__ import __version__

PROJECT = "api-fuzzer"


def get_version():
    """
    Provides name and version of the application
    :rtype: str
    """
    return "{} {}".format(PROJECT, __version__)
