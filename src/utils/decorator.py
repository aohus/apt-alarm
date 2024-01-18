import logging
import time
from functools import wraps


def time_logger(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start = time.time()
        result = func(self, *args, **kwargs)
        end = time.time()
        logging.info(f"[{func.__name__}] executed in: {end-start} seconds")
        return result

    return wrapper
