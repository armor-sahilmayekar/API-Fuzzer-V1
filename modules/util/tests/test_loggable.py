import logging

import pytest

from modules.util.loggable import Loggable  # Replace with the actual path


@pytest.fixture(autouse=True)
def reset_loggable():
    # Reset initialization state between tests
    Loggable._initialized = False
    yield
    Loggable._initialized = False


def test_loggable_logs_info(caplog):
    with caplog.at_level(logging.INFO):
        Loggable.info("Test info message")
    assert any("Test info message" in record.message and record.levelname == "INFO" for record in caplog.records)


def test_loggable_logs_debug_with_env_log_level(monkeypatch, caplog):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    with caplog.at_level(logging.DEBUG):
        Loggable.debug("Debug message")
    assert any("Debug message" in record.message and record.levelname == "DEBUG" for record in caplog.records)


def test_loggable_logs_warning(caplog):
    with caplog.at_level(logging.WARNING):
        Loggable.warning("This is a warning")
    assert any("This is a warning" in record.message and record.levelname == "WARNING" for record in caplog.records)


def test_loggable_logs_error(caplog):
    with caplog.at_level(logging.ERROR):
        Loggable.error("This is an error")
    assert any("This is an error" in record.message and record.levelname == "ERROR" for record in caplog.records)


def test_loggable_logs_critical(caplog):
    with caplog.at_level(logging.CRITICAL):
        Loggable.critical("This is critical")
    assert any("This is critical" in record.message and record.levelname == "CRITICAL" for record in caplog.records)


def test_loggable_exception_logging(caplog):
    with caplog.at_level(logging.ERROR):
        try:
            raise ValueError("Sample exception")
        except Exception:
            Loggable.exception("An exception occurred")
    assert any("An exception occurred" in record.message and record.levelname == "ERROR" for record in caplog.records)
    assert any("Traceback" in record.message or record.exc_info for record in caplog.records)


def test_logger_name_is_dynamic_for_class(caplog):
    class SampleClass:
        def do_log(self):
            Loggable.info("class scoped log")

    instance = SampleClass()
    with caplog.at_level(logging.INFO):
        instance.do_log()

    logger_names = {record.name for record in caplog.records}
    assert "SampleClass" in logger_names


def test_logger_name_defaults_to_applogger_outside_class(caplog):
    with caplog.at_level(logging.INFO):
        Loggable.info("top-level log")
    logger_names = {record.name for record in caplog.records}
    assert "AppLogger" in logger_names
