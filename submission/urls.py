from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

import submission.task.views
import submission.script.views
from submission import views

# Add default routes
router = DefaultRouter()
router.register(r'task', submission.task.views.TaskViewSet)
router.register(r'script', submission.script.views.ScriptViewSet)
router.register(r'token', views.TokenViewSet, basename='Token')

# Define file view
TaskFileView = submission.task.views.TaskViewSet.as_view({'get': 'file'})
# Define download view
TaskDownloadView = submission.task.views.TaskViewSet.as_view({'get': 'download'})

# Define URL patterns
urlpatterns = [
        # Register custom view for download
        re_path(r'^task/(?P<uuid>[^/.]+)/download/$', TaskDownloadView),
        # Register custom route for files
        re_path(r'^task/(?P<uuid>[^/.]+)/file/(?P<path>.*)$', TaskFileView),
        # Register default router
        path(r'', include(router.urls))
]
