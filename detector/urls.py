from django.urls import path
from . import views

app_name = 'detector'

urlpatterns = [
    path('', views.index, name='index'),
    path('result/<int:check_id>/', views.result, name='result'),
    path('about/', views.about, name='about'),
    path('api/check-news/', views.api_check_news, name='api_check_news'),
    path('debug/', views.debug_info, name='debug_info'),
]