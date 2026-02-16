"""
Custom middleware for error handling and request logging.
"""

import logging
import traceback
from django.http import JsonResponse
from django.conf import settings
import time


logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware:
    """
    Middleware to catch unhandled exceptions and return structured error responses.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as exc:
            # Log the full exception with traceback
            logger.error(
                f"Unhandled exception in {request.method} {request.path}: {str(exc)}",
                exc_info=True
            )
            
            # Return user-friendly error response
            if settings.DEBUG:
                # In debug mode, include detailed error information
                return JsonResponse({
                    'error': 'Internal Server Error',
                    'message': str(exc),
                    'traceback': traceback.format_exc(),
                    'path': request.path,
                    'method': request.method
                }, status=500)
            else:
                # In production, return generic error message
                return JsonResponse({
                    'error': 'Internal Server Error',
                    'message': 'Sorry, something went wrong. Please try again later.',
                    'request_id': id(request)
                }, status=500)


class RequestLoggingMiddleware:
    """
    Middleware to log incoming requests with timing information.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        # Log request start
        logger.info(f"Request started: {request.method} {request.path}")
        
        try:
            response = self.get_response(request)
            
            # Calculate duration
            duration = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Log request completion
            logger.info(
                f"Request completed: {request.method} {request.path} - "
                f"Status: {response.status_code}, Duration: {duration:.2f}ms"
            )
            
            return response
            
        except Exception as exc:
            duration = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed: {request.method} {request.path} - "
                f"Duration: {duration:.2f}ms, Error: {str(exc)}"
            )
            raise


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers to responses.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response
