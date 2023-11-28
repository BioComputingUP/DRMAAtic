from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter, SimpleRouter

import drmaatic.job.views
import drmaatic.task.views
from drmaatic import views

# Add default routes
router = SimpleRouter()
router.register(r'job', drmaatic.job.views.JobViewSet)
router.register(r'task', drmaatic.task.views.TaskViewSet)

TokenRetrieveView = drmaatic.views.retrieve_internal_token

JobFileView = drmaatic.job.views.JobViewSet.as_view({'get': 'file'})
JobDownloadView = drmaatic.job.views.JobViewSet.as_view({'get': 'download'})
JobStopView = drmaatic.job.views.JobViewSet.as_view({'put': 'stop'})
JobStatusView = drmaatic.job.views.JobViewSet.as_view({'get': 'status'})
JobAssignOwnershipView = drmaatic.job.views.JobViewSet.as_view({'put': 'assign_ownership'})

ExecutionTokenView = drmaatic.views.retrieve_execution_token

# Define URL patterns
urlpatterns = [
    re_path(r'^(?P<provider>[^/.]+)/token/$', TokenRetrieveView, name='retrieve internal token'),

    re_path(r'^job/(?P<uuid>[^/.]+)/download/$', JobDownloadView),
    re_path(r'^job/(?P<uuid>[^/.]+)/file/(?P<path>.*)$', JobFileView),
    re_path(r'^job/(?P<uuid>[^/.]+)/stop/$', JobStopView),
    re_path(r'^job/(?P<uuid>[^/.]+)/status/$', JobStatusView),
    re_path(r'^job/(?P<uuid>[^/.]+)/get_ownership/$', JobAssignOwnershipView),

    re_path(r'^execution-tokens/$', ExecutionTokenView, name='execution tokens'),

    path(r'', TemplateView.as_view(
        template_name='swagger-ui.html',
    ), name='openapi'),

    path(r'', include(router.urls)),
]

urlpatterns += staticfiles_urlpatterns()

