from django.urls import path
from .views import (
    index,
    api_webhook,
    embed_code,
    integration_guide,
    dashboard_stats,
    dashboard_view,
)
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/webhook/", api_webhook, name="api_webhook"),
    path("api/transcribe/", views.transcribe_audio, name="transcribe_audio"),
    path("embed/", embed_code, name="embed_code"),
    path("integrations/", integration_guide, name="integration_guide"),
    path("dashboard/", dashboard_view, name="dashboard_view"),
    path("dashboard/stats/", dashboard_stats, name="dashboard_stats"),
]
