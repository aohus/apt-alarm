import logging
from . import slackbot


def report_error(message: str, error_message: str):
    logging.error(message)
    slackbot.error(message, error_message)
