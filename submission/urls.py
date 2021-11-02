from django.urls import include, path
from rest_framework.routers import DefaultRouter

from submission import views

router = DefaultRouter()
router.register(r'task', views.TaskViewSet)  # TODO Implement views for jobs
router.register(r'script', views.ScriptViewSet)
router.register(r'params', views.ParamsViewSet)

# Define URL patterns
urlpatterns = [
        path('', include(router.urls))
]
