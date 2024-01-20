import logging
import time


class FmtTypes:
    DEFAULT = 0
    NO_FMT = 1
    TIME_ELAPSED = 2


class TimeElapsedFormatter(logging.Formatter):
    def __init__(self, fmt=None, date_fmt=None):
        super().__init__(fmt, date_fmt)
        self._start_time = 0.0
        self.fmt_in_use = FmtTypes.DEFAULT

    def set_start_time(self, start_time):
        self._start_time = start_time

    def formatTime(self, record, date_fmt=None):
        if self.fmt_in_use is FmtTypes.TIME_ELAPSED:
            return self.get_time_elapsed_str()
        return super().formatTime(record, date_fmt)

    def format(self, record):
        if self.fmt_in_use is FmtTypes.NO_FMT:
            return record.msg
        return super().format(record)

    def get_time_elapsed_str(self):
        if self._start_time == 0.0:
            self._start_time = time.time()
        elapsed_time = time.time() - self._start_time
        time_elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        return time_elapsed_str


class BaseLogger(logging.Logger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = kwargs.get("name", "Program")
        self.formatter = TimeElapsedFormatter('[%(asctime)s]: %(levelname)s:%(name)s:%(funcName)s: %(message)s')


class FileLogger(BaseLogger):
    def __init__(self, *args, log_file_path, log_level_file, **kwargs):
        super().__init__(*args, **kwargs)

        self.file_handler = None
        self.log_file_path = log_file_path
        if log_file_path is not None:
            self.file_handler = self._new_file_handler(log_level_file, log_file_path)
            self.addHandler(self.file_handler)

    def edit_file_logger(self, path, log_level=logging.DEBUG):
        if self.file_handler is not None:
            self.removeHandler(self.file_handler)
        self.log_file_path = path
        self.addHandler(self._new_file_handler(log_level, path))

    def _new_file_handler(self, log_level, path):
        self.log_file_path = path
        self.file_handler = logging.FileHandler(path)
        self.file_handler.setLevel(log_level)
        self.file_handler.setFormatter(self.formatter)
        return self.file_handler


class StreamLogger(BaseLogger):
    def __init__(self, *args, log_level_stream, **kwargs):
        super().__init__(*args, **kwargs)

        self.stream_handler = None
        self.stream_handler = self._new_stream_handler(log_level_stream)
        self.addHandler(self.stream_handler)

    def edit_stream_logger(self, log_level=logging.DEBUG):
        self.stream_handler.setLevel(log_level)

    def _new_stream_handler(self, log_level):
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(log_level)
        self.stream_handler.setFormatter(self.formatter)
        return self.stream_handler


class Logger(FileLogger, StreamLogger):
    def __init__(self, name=None, log_file_path=None, log_level_file=logging.DEBUG, log_level_stream=logging.INFO):
        super().__init__(
            name=name,
            log_file_path=log_file_path,
            log_level_file=log_level_file,
            log_level_stream=log_level_stream
        )
        self._started = 0

    def set_name_and_path(self, name, path, hard=0):
        if not self.name or hard:
            self.name = name
            self._started = 0
        if self.file_handler is None or hard:
            self.edit_file_logger(path)

    def program_start(self):
        if self._started:
            return
        self._started = 1
        self.formatter.fmt_in_use = FmtTypes.NO_FMT
        date_str = time.strftime("%Y-%m-%d")
        time_str = time.strftime("%H:%M:%S")
        self.info(f"\n[Date: {date_str} : Time: {time_str} : Program Name: {self.name}]")
        self.formatter.fmt_in_use = FmtTypes.TIME_ELAPSED

    def debug_no_fmt(self, msg, **kwargs):
        original = self.formatter.fmt_in_use
        self.formatter.fmt_in_use = FmtTypes.NO_FMT
        self.debug(msg, **kwargs)
        self.formatter.fmt_in_use = original


# _LOG_FILE_PATH = "general.log"
# _LOG_LEVEL_FILE = logging.DEBUG
# _LOG_LEVEL_STREAM = logging.INFO
# _LOG_NAME = "Logger"
logger = Logger()


# def _init_logger():
#     global logger
#     del logger
#     logger = Logger(_LOG_NAME, _LOG_FILE_PATH, _LOG_LEVEL_FILE, _LOG_LEVEL_STREAM)
#
#
# def logger_set_name_and_path(name: str, path: str):
#     global _LOG_FILE_PATH, _LOG_NAME
#     _LOG_FILE_PATH = path
#     _LOG_NAME = name
#     _init_logger()
#
#
# _init_logger()