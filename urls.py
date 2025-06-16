from django.urls import path
from . import views as core_views

urlpatterns = [
    path('dashboard-abertos/', core_views.dashboard_abertos, name='dashboard_abertos'),
] 