import logging
import logging.config
from pathlib import Path
from typing import Optional, List

from .settings import settings


class Logger:
    """
    Logging configuration utility for the Top Songs Dashboard project.
    Configures logging based on settings defined in .env file:
    - logs_dir: Directory for log files (relative to project root or absolute)
    - log_output: Where to send logs ("file", "console", or "both")
    """
    DEFAULT_LOG_LEVEL = "INFO"
    DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    DEFAULT_LOG_FILE = settings.logs_path / "app.log"

    @classmethod
    def setup(
        cls,
        log_level: Optional[str] = None,
        log_file: Optional[str] = None,
        log_format: Optional[str] = None,
        file_mode: str = "a",
        disable_existing_loggers: bool = False,
    ) -> None:
        """
        Set up logging configuration based on settings.

        Args:
            log_level (str, optional): Logging level (e.g., 'INFO', 'DEBUG').
            log_file (str, optional): Path to the log file.
            log_format (str, optional): Log message format.
            file_mode (str): File mode for log file ('a' for append, 'w' for overwrite).
            disable_existing_loggers (bool): Whether to disable existing loggers.
        """
        log_level = log_level or cls.DEFAULT_LOG_LEVEL
        log_format = log_format or cls.DEFAULT_LOG_FORMAT
        log_file = log_file or str(cls.DEFAULT_LOG_FILE)

        # Determine which handlers to use based on settings
        handlers: List[str] = []
        if settings.log_output in ["console", "both"]:
            handlers.append("console")
        if settings.log_output in ["file", "both"]:
            handlers.append("file")
            # Ensure log directory exists if file logging is enabled
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)

        logging_config = {
            "version": 1,
            "disable_existing_loggers": disable_existing_loggers,
            "formatters": {
                "default": {
                    "format": log_format,
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": log_level,
                },
                "file": {
                    "class": "logging.FileHandler",
                    "formatter": "default",
                    "level": log_level,
                    "filename": log_file,
                    "mode": file_mode,
                    "encoding": "utf-8",
                },
            },
            "root": {
                "handlers": handlers,
                "level": log_level,
            },
        }

        logging.config.dictConfig(logging_config)


def setup_logging():
    if settings.debug:
        Logger.setup(log_level="DEBUG")
    else:
        Logger.setup()
        

if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Hello, world!")
    print(f"Logs directory: {settings.logs_path}")
    print(f"Log output mode: {settings.log_output}")
    if "file" in settings.log_output:
        print(f"Log file location: {Logger.DEFAULT_LOG_FILE}")