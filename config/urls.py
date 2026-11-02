from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static

from accounts.views import (
    login_view, logout_view, home_router,
    admin_dashboard, engineer_dashboard, supervisor_dashboard,
    CurrentUserAPIView
)
from machines.views import (
    MachineListAPIView, ManualUploadAPIView,
    ManualListAPIView, ServeManualFileAPIView,
    ManualDeleteAPIView
)
from assistant.views import AskQuestionAPIView, RunHackathonDemosAPIView
from history.views import QuestionHistoryListAPIView, SupervisorStatsAPIView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Web UI Views
    path('', home_router, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('engineer-dashboard/', engineer_dashboard, name='engineer_dashboard'),
    path('supervisor-dashboard/', supervisor_dashboard, name='supervisor_dashboard'),

    # REST APIs
    path('api/auth/user/', CurrentUserAPIView.as_view(), name='api-current-user'),
    path('api/machines/', MachineListAPIView.as_view(), name='api-machines-list'),
    path('api/machines/register/', MachineListAPIView.as_view(), name='api-machine-register'),
    path('api/manuals/', ManualListAPIView.as_view(), name='api-manuals-list'),
    path('api/manuals/upload/', ManualUploadAPIView.as_view(), name='api-manual-upload'),
    path('api/manuals/<str:document_id>/pdf/', ServeManualFileAPIView.as_view(), name='api-manual-pdf'),
    path('api/manuals/<str:document_id>/page/<str:page>/', ServeManualFileAPIView.as_view(), name='api-manual-page'),
    path('api/manuals/<str:document_id>/delete/', ManualDeleteAPIView.as_view(), name='api-manual-delete'),
    path('api/ask/', AskQuestionAPIView.as_view(), name='api-ask'),
    path('api/history/', QuestionHistoryListAPIView.as_view(), name='api-history'),
    path('api/supervisor/logs/', QuestionHistoryListAPIView.as_view(), name='api-supervisor-logs'),
    path('api/supervisor/stats/', SupervisorStatsAPIView.as_view(), name='api-supervisor-stats'),
    path('api/demos/run/', RunHackathonDemosAPIView.as_view(), name='api-demos-run'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
