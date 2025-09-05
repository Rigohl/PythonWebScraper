import logging
from PyQt6.QtCore import pyqtSignal, QObject

class QtLogSignalEmitter(QObject):
    log_record = pyqtSignal(str, str, str)  # level, name, message

class QtLogHandler(logging.Handler):
    def __init__(self, emitter: QtLogSignalEmitter):
        super().__init__()
        self.emitter = emitter

    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
            self.emitter.log_record.emit(record.levelname, record.name, msg)
        except Exception:
            pass
