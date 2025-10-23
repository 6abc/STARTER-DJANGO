from django.urls import path
from app1 import views

urlpatterns = [
    path('app/', views.app_view, name='app'),
]