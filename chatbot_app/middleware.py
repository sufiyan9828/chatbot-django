"""
Custom middleware for rate limiting and input validation.
"""

import time
import logging
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """
    Leaky Bucket rate limiting middleware based on IP address.
    Smooths out bursts and ensures a steady rate of processing.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Capacity of the bucket (max burst)
        self.capacity = getattr(settings, "RATE_LIMIT_CAPACITY", 5)
        # Leak rate (tokens per minute)
        self.leak_rate = getattr(settings, "RATE_LIMIT_LEAK_RATE", 10)

    def __call__(self, request):
        # Only apply to chat endpoints
        if request.method == "POST" and (
            request.path == "/" or request.path == "/api/webhook/"
        ):
            client_ip = self.get_client_ip(request)
            cache_key = f"leaky_bucket_{client_ip}"

            # Bucket state: (tokens, last_update_time)
            bucket = cache.get(cache_key, (self.capacity, time.time()))
            tokens, last_update = bucket

            # 1. Leak tokens based on elapsed time
            now = time.time()
            elapsed = now - last_update
            # Refill rate is leak_rate/60 tokens per second
            refill = elapsed * (self.leak_rate / 60.0)
            tokens = min(self.capacity, tokens + refill)

            # 2. Check if we have tokens to consume
            if tokens < 1:
                logger.warning(
                    f"Rate limit exceeded (Leaky Bucket) for IP: {client_ip}"
                )
                return JsonResponse(
                    {
                        "message": "Too many requests. Please wait a moment.",
                        "error": True,
                    },
                    status=429,
                )

            # 3. Consume a token and update bucket
            tokens -= 1
            cache.set(
                cache_key, (tokens, now), 3600
            )  # Expire after 1 hour of inactivity

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class InputValidationMiddleware:
    """
    Middleware to validate input data before processing.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only apply to POST requests (chat messages)
        if request.method == "POST" and request.path == "/":
            user_input = request.POST.get("user-input", "").strip()

            # Validate input
            validation_error = self.validate_input(user_input)
            if validation_error:
                logger.warning(f"Input validation failed: {validation_error}")
                return JsonResponse(
                    {"message": validation_error, "error": True}, status=400
                )

        response = self.get_response(request)
        return response

    def validate_input(self, user_input):
        """Validate user input and return error message if invalid."""

        # Check if input is empty
        if not user_input:
            return "Message cannot be empty."

        # Check minimum length
        if len(user_input) < 1:
            return "Message is too short."

        # Check maximum length (prevent very long messages)
        if len(user_input) > 1000:
            return "Message is too long. Please keep it under 1000 characters."

        # Check for potential injection attempts
        dangerous_patterns = [
            "<script",
            "</script>",
            "javascript:",
            "onload=",
            "onerror=",
            "eval(",
            "exec(",
            "system(",
            "import os",
            "__import__",
        ]

        user_input_lower = user_input.lower()
        for pattern in dangerous_patterns:
            if pattern in user_input_lower:
                logger.warning(f"Potentially dangerous input detected: {pattern}")
                return (
                    "Message contains invalid characters. Please rephrase your message."
                )

        return None
