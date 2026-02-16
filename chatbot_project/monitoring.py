"""
Enhanced monitoring middleware for request/response logging and metrics.
"""

import logging
import time
import psutil
from django.http import JsonResponse
from django.utils import timezone
from django.db import connection
from chatbot_app.models import AIServiceUsage, SystemMetrics

logger = logging.getLogger(__name__)


class DetailedLoggingMiddleware:
    """
    Enhanced middleware for detailed request/response logging.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        # Log request details
        request_data = {
            'method': request.method,
            'path': request.path,
            'ip': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown')[:200],
            'content_length': len(request.body) if hasattr(request, 'body') else 0,
        }
        
        logger.info(f"Request started: {request_data}")
        
        try:
            response = self.get_response(request)
            
            # Calculate duration
            duration = (time.time() - start_time) * 1000
            
            # Log response details
            response_data = {
                'status_code': response.status_code,
                'duration_ms': round(duration, 2),
                'response_size': len(response.content) if hasattr(response, 'content') else 0,
            }
            
            logger.info(f"Request completed: {request_data['method']} {request_data['path']} - "
                       f"Status: {response_data['status_code']}, Duration: {response_data['duration_ms']}ms")
            
            # Log AI service usage for chat requests
            if request.method == 'POST' and request.path == '/' and response.status_code == 200:
                self._log_ai_service_usage(request, response, duration)
            
            return response
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"Request failed: {request_data['method']} {request_data['path']} - "
                        f"Duration: {duration:.2f}ms, Error: {str(e)}")
            raise
    
    def get_client_ip(self, request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _log_ai_service_usage(self, request, response, duration):
        """Log AI service usage for monitoring."""
        try:
            # Try to parse response to determine if fallback was used
            if hasattr(response, 'content'):
                import json
                try:
                    response_data = json.loads(response.content.decode('utf-8'))
                    is_fallback = response_data.get('fallback', False)
                    service_name = 'fallback' if is_fallback else 'gemini'  # Simplified detection
                except:
                    service_name = 'unknown'
                    is_fallback = False
            else:
                service_name = 'unknown'
                is_fallback = False
            
            # Update or create AI service usage record
            usage_record, created = AIServiceUsage.objects.get_or_create(
                service_name=service_name,
                defaults={
                    'model_used': 'unknown',
                    'request_count': 0,
                    'success_count': 0,
                    'error_count': 0,
                }
            )
            
            usage_record.update_usage(
                success=response.status_code == 200,
                response_time_ms=int(duration)
            )
            
        except Exception as e:
            logger.warning(f"Failed to log AI service usage: {str(e)}")


class MetricsCollectionMiddleware:
    """
    Middleware to collect system metrics periodically.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.last_metrics_time = time.time()
        self.metrics_interval = 300  # Collect metrics every 5 minutes
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Check if it's time to collect metrics
        current_time = time.time()
        if current_time - self.last_metrics_time >= self.metrics_interval:
            self._collect_system_metrics()
            self.last_metrics_time = current_time
        
        return response
    
    def _collect_system_metrics(self):
        """Collect and store system performance metrics."""
        try:
            # Get system metrics
            memory_info = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get database metrics
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM chatbot_app_chatsession")
                active_sessions = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM chatbot_app_chatmessage")
                total_messages = cursor.fetchone()[0]
            
            # Store metrics
            SystemMetrics.objects.create(
                active_sessions=active_sessions,
                total_messages=total_messages,
                memory_usage_mb=memory_info.used / (1024 * 1024),
                cpu_usage_percent=cpu_percent,
            )
            
            logger.info(f"System metrics collected: {active_sessions} sessions, "
                       f"{total_messages} messages, Memory: {memory_info.percent:.1f}%, "
                       f"CPU: {cpu_percent:.1f}%")
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {str(e)}")


class SecurityMonitoringMiddleware:
    """
    Middleware for security monitoring and anomaly detection.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.suspicious_patterns = [
            '<script', 'javascript:', 'onload=', 'onerror=', 
            'eval(', 'exec(', 'system(', '__import__',
            'union select', 'drop table', 'insert into',
        ]
    
    def __call__(self, request):
        # Monitor for suspicious activity
        if request.method == 'POST':
            self._check_suspicious_content(request)
        
        response = self.get_response(request)
        
        # Monitor response for data leaks
        if response.status_code == 200:
            self._check_data_exposure(request, response)
        
        return response
    
    def _check_suspicious_content(self, request):
        """Check request content for suspicious patterns."""
        try:
            content = request.body.decode('utf-8', errors='ignore').lower()
            user_input = request.POST.get('user-input', '').lower()
            
            for pattern in self.suspicious_patterns:
                if pattern in content or pattern in user_input:
                    ip = self.get_client_ip(request)
                    logger.warning(f"Suspicious pattern detected from {ip}: {pattern}")
                    
                    # Could implement IP blocking here
                    break
        except Exception as e:
            logger.debug(f"Error checking suspicious content: {str(e)}")
    
    def _check_data_exposure(self, request, response):
        """Check response for potential data exposure."""
        try:
            if hasattr(response, 'content'):
                content = response.content.decode('utf-8', errors='ignore').lower()
                
                # Check for potential sensitive data exposure
                sensitive_patterns = [
                    'password', 'secret', 'token', 'api_key',
                    'private_key', 'database', 'admin'
                ]
                
                for pattern in sensitive_patterns:
                    if pattern in content and 'error' in content:
                        logger.warning(f"Potential data exposure in response: {pattern}")
                        break
        except Exception as e:
            logger.debug(f"Error checking data exposure: {str(e)}")
    
    def get_client_ip(self, request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
