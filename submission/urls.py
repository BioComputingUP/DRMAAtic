from django.conf.urls import url
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from submission import views

# Add default routes
router = DefaultRouter()
router.register(r'task', views.TaskViewSet)
router.register(r'script', views.ScriptViewSet)
router.register(r'params', views.ParamsViewSet)
# router.register(r'user', views.UserViewSet)
router.register(r'token', views.TokenViewSet, basename='Token')

# Define file view
TaskFileView = views.TaskViewSet.as_view({'get': 'file'})
# Define download view
TaskDownloadView = views.TaskViewSet.as_view({'get': 'download'})

# Define URL patterns
urlpatterns = [
        # Register custom view for download
        url(r'^task/(?P<uuid>[^/.]+)/download/$', TaskDownloadView),
        # Register custom route for files
        url(r'^task/(?P<uuid>[^/.]+)/file/(?P<path>.*)$', TaskFileView),
        # Register default router
        path(r'', include(router.urls))
]
