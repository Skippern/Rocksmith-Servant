import time

from utils import logger


class Debugger:
    def __init__(self, config_data):
        self.debug = config_data.debugger.debug
        self.interval = config_data.debugger.interval

        self.last_log = 0

    def log(self, message):
        if self.debug:
            logger.debug("[DEBUG] " + message)

    def log_on_interval(self, message):
        if self.last_log + self.interval < time.time():
            self.log(message)
            self.last_log = time.time()
