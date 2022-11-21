import logging

LOG_FORMAT = '%(asctime)s | %(levelname)s | %(name)s:%(lineno)s | %(message)s'


def setup_logging(name: str, log_level: str = 'DEBUG') -> logging.Logger:
    """Return Logger class to set up logging for the project."""
    logging.basicConfig(format=LOG_FORMAT, level=log_level)
    return logging.getLogger(name)
