#top.dwgx.utils.loggerutils

import logging
from PyQt6.QtCore import QObject, pyqtSignal
class LogEmitter(QObject):
    log_signal = pyqtSignal(str, str)  # level, message

class QtLoggingHandler(logging.Handler):
    def __init__(self, log_emitter):
        super().__init__()
        self.log_emitter = log_emitter

    def emit(self, record):
        msg = self.format(record)
        self.log_emitter.log_signal.emit(record.levelname, msg)

def setup_logger(name, log_emitter):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = QtLoggingHandler(log_emitter)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
