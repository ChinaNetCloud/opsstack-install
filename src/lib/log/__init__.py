import logging


class Logger:
    def __init__(self, file_path, level):
        self.logger = logging.getLogger()
        self.formatter = logging.Formatter('[%(asctime)s]: %(message)s')
        self.handler = logging.FileHandler(file_path)
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
        if level == "debug":
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    def log(self, msg):
        try:
            self.logger.info(unicode(msg))
        except NameError:
            self.logger.info(msg)

    def debug(self, msg):
        try:
            self.logger.debug(unicode(msg))
        except NameError:
            self.logger.debug(msg)


__logger = None


def get_logger(file_path=None, level=None):
    global __logger
    if __logger is None:
        __logger = Logger(file_path, level)
    return __logger
