from django.urls import include, path
from rest_framework.routers import DefaultRouter

from submission import views

# Register routes
router = DefaultRouter()
router.register(r'task', views.TaskViewSet)  # TODO Implement views for jobs
router.register(r'script', views.ScriptViewSet)

# Define URL patterns
urlpatterns = [
        path('', include(router.urls))
]
