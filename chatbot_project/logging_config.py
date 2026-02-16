"""
Logging configuration for the chatbot project.
Provides structured logging with timestamps and context.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured log output."""
    
    def format(self, record):
        timestamp = datetime.utcnow().isoformat() + 'Z'
        level = record.levelname
        module = record.module
        function = record.funcName
        line = record.lineno
        message = record.getMessage()
        
        # Add exception info if present
        exception_info = ''
        if record.exc_info:
            exception_info = f' | Exception: {self.formatException(record.exc_info)}'
        
        return f"[{timestamp}] {level} | {module}:{function}:{line} | {message}{exception_info}"


def setup_logging():
    """Configure logging for the application."""
    
    # Create logs directory if it doesn't exist
    logs_dir = Path(__file__).parent.parent / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(console_handler)
    
    # File handler for errors
    error_file_handler = logging.FileHandler(logs_dir / 'errors.log')
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(error_file_handler)
    
    # File handler for all logs
    debug_file_handler = logging.FileHandler(logs_dir / 'debug.log')
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(debug_file_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger('django.db.backends').setLevel(logging.WARNING)
    logging.getLogger('whitenoise').setLevel(logging.WARNING)
    logging.getLogger('google').setLevel(logging.WARNING)
    
    return root_logger
