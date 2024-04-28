import logging
import os
from logging.handlers import TimedRotatingFileHandler

LOG_FORMAT = "[%(asctime)s]: %(levelname)s - %(message)s"


class CustomLogFormatterFile(logging.Formatter):

    FORMATS = {
        logging.DEBUG: LOG_FORMAT,
        logging.INFO: LOG_FORMAT,
        logging.WARNING: LOG_FORMAT,
        logging.ERROR: LOG_FORMAT,
        logging.CRITICAL: LOG_FORMAT
    }

    def format(self, message):
        log_fmt = self.FORMATS.get(message.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(message)


class CustomLogFormatterConsole(logging.Formatter):
    green = "\x1b[32m"
    magenta = "\x1b[95m"
    cyan = "\x1b[96m"
    yellow = "\x1b[93m"
    red = "\x1b[31m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: magenta + LOG_FORMAT + reset,
        logging.INFO: green + LOG_FORMAT + reset,
        logging.WARNING: yellow + LOG_FORMAT + reset,
        logging.ERROR: red + LOG_FORMAT + reset,
        logging.CRITICAL: bold_red + LOG_FORMAT + reset
    }

    def format(self, message):
        log_fmt = self.FORMATS.get(message.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(message)


logging_stream_handler = logging.StreamHandler()
logging_stream_handler.setLevel(logging.INFO)
logging_stream_handler.setFormatter(CustomLogFormatterConsole())

if not os.path.exists('logs'):
    os.mkdir("logs")

file_path = os.path.join('logs', 'server.log')
file_handler = TimedRotatingFileHandler(file_path, when="midnight", interval=1, backupCount=7, encoding='utf-8')
file_handler.suffix = "%Y-%m-%d"
file_handler.setFormatter(CustomLogFormatterFile())


logger = logging.root
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(logging_stream_handler)


def debug(*param):
    logger.debug(*param)


def info(*param):
    logger.info(*param)


def warning(*param):
    logger.warning(*param)


def error(*param):
    logger.error(*param)


def critical(*param):
    logger.critical(*param)


def exception(*param):
    logger.exception(*param)


