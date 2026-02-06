from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'meeting'

router = DefaultRouter()
router.register(r'api/meetings', views.MeetingViewSet, basename='meeting')

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_meeting, name='create_meeting'),
    path('meeting/<int:meeting_id>/', views.meeting_result, name='meeting_result'),
    path('history/', views.meeting_history, name='meeting_history'),
    path('', include(router.urls)),
]
