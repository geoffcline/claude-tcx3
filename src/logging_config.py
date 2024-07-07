import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler
import os
import sys


class NewLineStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            if record.levelno >= logging.WARNING:
                stream.write(self.terminator)
            stream.write(msg)
            stream.write(self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)


def setup_logging(log_level=logging.INFO, log_dir='logs'):
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture all log levels

    # Remove all existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console handler for warnings and errors (always enabled)
    console_handler = NewLineStreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)
    root_logger.addHandler(console_handler)

    # File handler (thread-safe, for all log levels)
    try:
        file_handler = ConcurrentRotatingFileHandler(
            f"{log_dir}/markdown_processor.log",
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)  # Capture all log levels
        root_logger.addHandler(file_handler)
    except Exception as e:
        root_logger.error(f"Failed to set up file logging: {e}")

    return root_logger