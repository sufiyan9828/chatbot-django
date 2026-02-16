from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class ChatSession(models.Model):
    """Model to track chat sessions."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="chat_sessions",
    )
    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    message_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["session_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Session {self.session_id} ({self.message_count} messages)"

    def increment_message_count(self):
        """Increment the message count."""
        self.message_count += 1
        self.save(update_fields=["message_count", "updated_at"])


class ChatMessage(models.Model):
    """Model to store individual chat messages."""

    MESSAGE_TYPES = [
        ("user", "User Message"),
        ("bot", "Bot Message"),
        ("system", "System Message"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="chat_messages",
    )
    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="messages"
    )
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_fallback = models.BooleanField(default=False)
    ai_service_used = models.CharField(max_length=50, null=True, blank=True)
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["timestamp"]
        indexes = [
            models.Index(fields=["session", "timestamp"]),
            models.Index(fields=["message_type"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."


class AIServiceUsage(models.Model):
    """Model to track AI service usage and performance."""

    SERVICE_CHOICES = [
        ("gemini", "Google Gemini"),
        ("openrouter", "OpenRouter"),
        ("fallback", "Fallback System"),
    ]

    service_name = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    model_used = models.CharField(max_length=100, null=True, blank=True)
    request_count = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    error_count = models.PositiveIntegerField(default=0)
    avg_response_time_ms = models.FloatField(null=True, blank=True)
    last_used = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-last_used"]
        indexes = [
            models.Index(fields=["service_name"]),
            models.Index(fields=["last_used"]),
        ]

    def __str__(self):
        return (
            f"{self.service_name}: {self.success_count}/{self.request_count} successful"
        )

    def update_usage(self, success: bool, response_time_ms: int = None):
        """Update usage statistics."""
        self.request_count += 1
        if success:
            self.success_count += 1
        else:
            self.error_count += 1

        if response_time_ms is not None:
            if self.avg_response_time_ms is None:
                self.avg_response_time_ms = response_time_ms
            else:
                # Calculate rolling average
                self.avg_response_time_ms = (
                    self.avg_response_time_ms * (self.request_count - 1)
                    + response_time_ms
                ) / self.request_count

        self.save(
            update_fields=[
                "request_count",
                "success_count",
                "error_count",
                "avg_response_time_ms",
                "last_used",
            ]
        )


class SystemMetrics(models.Model):
    """Model to store system performance metrics."""

    timestamp = models.DateTimeField(auto_now_add=True)
    active_sessions = models.PositiveIntegerField(default=0)
    total_messages = models.PositiveIntegerField(default=0)
    memory_usage_mb = models.FloatField(null=True, blank=True)
    cpu_usage_percent = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"Metrics at {self.timestamp}: {self.total_messages} messages"
