from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

import submission.job.views
import submission.task.views
from submission import views

# Add default routes
router = DefaultRouter()
router.register(r'job', submission.job.views.JobViewSet)
router.register(r'task', submission.task.views.TaskViewSet)
router.register(r'token', views.TokenViewSet, basename='Token')

# Define file view
JobFileView = submission.job.views.JobViewSet.as_view({'get': 'file'})
# Define download view
JobDownloadView = submission.job.views.JobViewSet.as_view({'get': 'download'})
# Define stop view
JobStopView = submission.job.views.JobViewSet.as_view({'put': 'stop'})

# Define URL patterns
urlpatterns = [
        # Register custom view for download
        re_path(r'^job/(?P<uuid>[^/.]+)/download/$', JobDownloadView),
        # Register custom route for files
        re_path(r'^job/(?P<uuid>[^/.]+)/file/(?P<path>.*)$', JobFileView),
        # Register custom route for stop
        re_path(r'^job/(?P<uuid>[^/.]+)/stop/$', JobStopView),
        # Register default router
        path(r'', include(router.urls))
]
