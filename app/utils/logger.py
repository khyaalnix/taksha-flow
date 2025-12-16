import atexit
import datetime
import pathlib
from typing import Dict, Optional, Union, Any
import json
import os
import logging
import logging.config

from bson import ObjectId
from pydantic import BaseModel, model_validator
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

from app.utils.utility import SingleTonClass

appName = "app.warning" if os.getenv("LOG_LEVEL") == "WARNING" else (
            "app" if os.getenv("LOG_LEVEL") == "INFO" else ""
)

class LogConfig(BaseModel):
    app_name: str = appName
    config_file: Union[str, pathlib.Path]
    default_level: Union[int, str] = os.getenv("LOG_LEVEL")
    extra_fields: Dict[str, Any] = None

    @property
    def config_path(self):
        return pathlib.Path(self.config_file) if isinstance(self.config_file, str) else self.config_file

class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

class JSONFormatter(logging.Formatter):
    BUILTIN_ATTRS = {
        "args", "asctime", "created", "exc_info", "exc_text", "filename",
        "funcName", "levelname", "levelno", "lineno", "module", "msecs",
        "message", "msg", "name", "pathname", "process", "processName",
        "relativeCreated", "stack_info", "thread", "threadName", "taskName"
    }
    TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    def __init__(self, *, fmt_keys: Optional[Dict[str, str]]= None):
        super().__init__()
        self.fmt_keys = fmt_keys or {}

    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        return json.dumps(message, cls=CustomEncoder)

    def _prepare_log_dict(self, record: logging.LogRecord):
        base_fields = {
            "message": record.getMessage(),
            "timestamp": datetime.datetime.fromtimestamp(
                record.created, tz=datetime.timezone.utc
            ).strftime(self.TIME_FORMAT),
            "level": record.levelname,
            "logger": record.name
        }

        # Handle exceptions and stack traces
        if record.exc_info:
            base_fields["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            base_fields["stack_info"] = self.formatStack(record.stack_info)

        # Add custom formatted fields
        custom_fields = {
            key: base_fields.pop(val, getattr(record, val, None))
            for key, val in self.fmt_keys.items()
        }

        # Add extra fields from record
        extra_fields = {
            key: val
            for key, val in record.__dict__.items()
            if key not in self.BUILTIN_ATTRS and not key.startswith("_")
        }
        return {
            **base_fields,
            **custom_fields,
            **extra_fields,
            **(getattr(record, "extra", {}))
        }

class NonErrorFilter(logging.Filter):
    def filter(self, record: logging.LogRecord):
        return record.levelno < logging.INFO


def _setup_queue(logger: logging.Logger):
    queue = Queue()
    queue_handler = QueueHandler(queue)
    handlers = logger.handlers[:]
    for handler in handlers:
        logger.removeHandler(handler)

    listener = QueueListener(queue,*handlers,respect_handler_level=True)
    logger.addHandler(queue_handler)
    listener.start()
    atexit.register(listener.stop)


class LoggerFactory(SingleTonClass):

    def __init__(self, ):
        if not hasattr(self, '_initialized'):
            self.log_instances: Dict[str, logging.Logger] = {}
            self.config = None
            self._initialized = True

    def get_logger(self, config: LogConfig = None, create_queue: bool = True) -> logging.Logger:
        _default_config = "configs/logConfig.json"
        self.config = LogConfig(config_file=_default_config) if config is None else config

        if self.config.app_name in self.log_instances:
            return self.log_instances[self.config.app_name]

        logger = self._setup_logger(self.config, create_queue)
        self.log_instances[self.config.app_name] = logger
        return self.log_instances[self.config.app_name]

    @staticmethod
    def _setup_logger(config: LogConfig, create_queue: bool):
        logger = logging.getLogger(config.app_name)
        try:
            with open(config.config_path,'r') as file:
                log_config = json.load(file)
                logging.config.dictConfig(log_config)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.setLevel(config.default_level)
            handler = logging.StreamHandler()
            handler.setFormatter(JSONFormatter())
            logger.addHandler(handler)
            logger.warning(f"Failed to load logging config: {str(e)}. Using defaults.")
            return logger
        except Exception as e:
            print(f"Error setting up logger: {str(e)}")

        if create_queue:
            _setup_queue(logger)
        return logger

