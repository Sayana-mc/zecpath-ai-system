import logging
from utils.logger import get_logger


def test_logging():
    logger = get_logger("test_zecpath_logger")
    assert isinstance(logger, logging.Logger)
    logger.info("Zecpath AI system test started")
    logger.info("Logging system test completed")
    assert len(logger.handlers) > 0
