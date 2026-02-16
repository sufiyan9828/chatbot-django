"""
System views for health checks and monitoring.
"""

import logging
from django.http import JsonResponse
from django.db import connection
from django.conf import settings
from django.utils import timezone
import os
import psutil

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.
    Returns system status including database connectivity.
    """
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "unhealthy"
    
    # Check environment variables
    env_status = "healthy"
    missing_vars = []
    required_vars = ["GEMINI_API_KEY"]
    
    for var in required_vars:
        if not os.getenv(var):
            env_status = "unhealthy"
            missing_vars.append(var)
    
    # System metrics
    try:
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        
        system_metrics = {
            "memory_usage_percent": memory_info.percent,
            "disk_usage_percent": disk_info.percent,
            "cpu_count": psutil.cpu_count(),
        }
    except Exception as e:
        logger.warning(f"Could not collect system metrics: {str(e)}")
        system_metrics = {}
    
    # Overall status
    overall_status = "healthy" if db_status == "healthy" and env_status == "healthy" else "unhealthy"
    
    response_data = {
        "status": overall_status,
        "timestamp": timezone.now().isoformat(),
        "version": "1.0.0",
        "checks": {
            "database": db_status,
            "environment": env_status,
        },
        "system": system_metrics,
    }
    
    if missing_vars:
        response_data["checks"]["missing_environment_variables"] = missing_vars
    
    status_code = 200 if overall_status == "healthy" else 503
    
    return JsonResponse(response_data, status=status_code)


def system_info(request):
    """
    Detailed system information endpoint for debugging.
    Only available in DEBUG mode.
    """
    if not settings.DEBUG:
        return JsonResponse({"error": "Not available in production"}, status=404)
    
    try:
        # Django settings info
        settings_info = {
            "DEBUG": settings.DEBUG,
            "ALLOWED_HOSTS": settings.ALLOWED_HOSTS,
            "DATABASE_ENGINE": settings.DATABASES["default"]["ENGINE"],
            "INSTALLED_APPS_COUNT": len(settings.INSTALLED_APPS),
            "MIDDLEWARE_COUNT": len(settings.MIDDLEWARE),
        }
        
        # Request info
        request_info = {
            "method": request.method,
            "path": request.path,
            "scheme": request.scheme,
            "is_secure": request.is_secure(),
            "content_type": request.content_type,
        }
        
        return JsonResponse({
            "django_settings": settings_info,
            "request_info": request_info,
            "timestamp": timezone.now().isoformat(),
        })
        
    except Exception as e:
        logger.error(f"System info endpoint failed: {str(e)}")
        return JsonResponse({
            "error": "Failed to collect system information",
            "details": str(e) if settings.DEBUG else None
        }, status=500)
