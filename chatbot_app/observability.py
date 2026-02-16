"""
Observability module for the chatbot.
Handles tracing and monitoring using Langfuse (or other providers in the future).
"""

import os
import functools
import logging
from typing import Optional, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)

# Try to import langfuse
try:
    from langfuse import Langfuse
    from langfuse.decorators import observe, langfuse_context

    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    logger.warning("Langfuse not installed. tracing will be disabled.")


class ObservabilityService:
    """
    Manages observability and tracing.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ObservabilityService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the observability provider."""
        self.enabled = False
        self.langfuse = None

        if not LANGFUSE_AVAILABLE:
            return

        # Check for keys in settings or environment
        public_key = getattr(settings, "LANGFUSE_PUBLIC_KEY", None) or os.environ.get(
            "LANGFUSE_PUBLIC_KEY"
        )
        secret_key = getattr(settings, "LANGFUSE_SECRET_KEY", None) or os.environ.get(
            "LANGFUSE_SECRET_KEY"
        )
        host = getattr(
            settings, "LANGFUSE_HOST", "https://cloud.langfuse.com"
        ) or os.environ.get("LANGFUSE_HOST")

        if public_key and secret_key:
            try:
                self.langfuse = Langfuse(
                    public_key=public_key, secret_key=secret_key, host=host
                )
                self.enabled = True
                logger.info("Langfuse observability initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Langfuse: {e}")
        else:
            logger.info("Langfuse keys not found. Observability disabled.")

    def trace(self, **kwargs):
        """
        Decorator to trace a function.
        Usage:
            @observability.trace(name="my_function")
            def my_function(): ...
        """

        def decorator(func):
            if not self.enabled:
                return func

            # Use Langfuse's native decorator if available
            # We wrap it to handle our custom logic if needed
            @observe(**kwargs)
            @functools.wraps(func)
            def wrapper(*args, **func_kwargs):
                return func(*args, **func_kwargs)

            return wrapper

        return decorator

    def flush(self):
        """Flush any buffered events."""
        if self.enabled and self.langfuse:
            try:
                self.langfuse.flush()
            except Exception as e:
                logger.error(f"Failed to flush Langfuse: {e}")


# Global instance
observability = ObservabilityService()
