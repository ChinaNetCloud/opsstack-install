import logging
from logging.handlers import MemoryHandler


class Logger:
    def __init__(self):
        self.logger = logging.getLogger()
        self.buffer = MemoryHandler(1000)
        self.handler = None
        self.formatter = logging.Formatter('[%(asctime)s]: %(message)s')
        self.buffer.setFormatter(self.formatter)
        self.logger.addHandler(self.buffer)
        self.logger.setLevel(logging.DEBUG)

    def log(self, msg):
        try:
            self.logger.info(unicode(msg))
        except NameError:
            self.logger.info(msg)
        if self.handler is not None:
            self.buffer.flush()

    def set_log_file(self, path):
        self.handler = logging.FileHandler(path)
        self.handler.setFormatter(self.formatter)
        self.buffer.setTarget(self.handler)
        self.buffer.flush()


__logger = None


def get_logger():
    global __logger
    if __logger is None:
        __logger = Logger()
    return __logger
