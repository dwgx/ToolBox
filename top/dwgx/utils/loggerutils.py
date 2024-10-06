import logging
from PySide6.QtCore import QObject, Signal

class LogEmitter(QObject):
    # 使用 PySide6 中的 Signal
    log_signal = Signal(str, str)

def setup_logger(name, log_emitter=None):
    """
    设置并返回一个日志记录器。
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 确保 logger 只有一个处理程序
    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if log_emitter:
        # 创建一个自定义的日志处理程序，将日志通过信号发送
        class LogEmitterHandler(logging.Handler):
            def __init__(self, emitter):
                super().__init__()
                self.emitter = emitter

            def emit(self, record):
                msg = self.format(record)
                self.emitter.log_signal.emit(record.levelname, msg)

        emitter_handler = LogEmitterHandler(log_emitter)
        emitter_handler.setFormatter(formatter)
        logger.addHandler(emitter_handler)

    return logger
