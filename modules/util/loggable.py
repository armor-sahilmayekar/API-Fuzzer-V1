import logging
import sys
import inspect
import os

class Loggable:
    """
    Loggable is a static logging utility class that provides consistent logging
    across modules. The logger name is dynamically set based on the calling class.
    The logging level can be dynamically set using the 'LOG_LEVEL' environment variable.

    Usage:
    ------
    from loggable import Loggable

    Loggable.info("Starting app...")  # Logs with the calling class name as logger name
    Loggable.error("Something went wrong")  # Automatically uses the calling class's name

    Features:
    ---------
    - Static logging methods: debug, info, warning, error, critical
    - Dynamically named logger based on the calling class
    - Logs to stdout
    - One-time initialization of logging
    - Dynamic log level based on 'LOG_LEVEL' environment variable
    """

    _initialized = False

    @staticmethod
    def _init_logger():
        if not Loggable._initialized:
            # Get the log level from the environment variable, default to INFO if not set
            log_level = os.getenv("LOG_LEVEL", "INFO").upper()
            log_level = getattr(logging, log_level, logging.INFO)

            logging.basicConfig(
                level=log_level,
                format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
                stream=sys.stdout
            )
            Loggable._initialized = True

    @staticmethod
    def get_logger():
        """
        Dynamically fetches the calling class's name to set the logger name.
        If not called within a class, defaults to 'AppLogger'.
        """
        Loggable._init_logger()
        # Get the calling class name dynamically
        frame = inspect.stack()[2]
        calling_class = frame[0].f_locals.get('self', None)
        if calling_class:
            class_name = calling_class.__class__.__name__
        else:
            class_name = "AppLogger"  # Default if not in a class context
        return logging.getLogger(class_name)

    @staticmethod
    def debug(msg):
        """Logs a debug message"""
        Loggable.get_logger().debug(msg)

    @staticmethod
    def info(msg):
        """Logs an info message"""
        Loggable.get_logger().info(msg)

    @staticmethod
    def warning(msg):
        """Logs a warning message"""
        Loggable.get_logger().warning(msg)

    @staticmethod
    def error(msg):
        """Logs an error message"""
        Loggable.get_logger().error(msg)

    @staticmethod
    def critical(msg):
        """Logs a critical message"""
        Loggable.get_logger().critical(msg)

    @staticmethod
    def exception(msg):
        """Logs an exception with a traceback"""
        Loggable.get_logger().exception(msg)
