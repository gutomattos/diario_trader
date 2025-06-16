from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('trades/', views.trade_list, name='trade_list'),
    path('trades/novo/', views.trade_create, name='trade_create'),
    path('ibov/', views.ibov_list, name='ibov_list'),
    path('ibov/novo/', views.ibov_create, name='ibov_create'),
    path('cdi/', views.cdi_list, name='cdi_list'),
    path('cdi/novo/', views.cdi_create, name='cdi_create'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('trades/editar/<int:trade_id>/', views.trade_edit, name='trade_edit'),
    path('trades/deletar/<int:trade_id>/', views.trade_delete, name='trade_delete'),
    path('trades/deletar-multiplos/', views.trade_delete_multiple, name='trade_delete_multiple'),
    path('ibov/<int:ibov_id>/editar/', views.ibov_edit, name='ibov_edit'),
    path('ibov/<int:ibov_id>/deletar/', views.ibov_delete, name='ibov_delete'),
    path('cdi/<int:cdi_id>/editar/', views.cdi_edit, name='cdi_edit'),
    path('cdi/<int:cdi_id>/deletar/', views.cdi_delete, name='cdi_delete'),
    path('aporte/', views.aporte_list, name='aporte_list'),
    path('aporte/novo/', views.aporte_create, name='aporte_create'),
    path('retirada/', views.retirada_list, name='retirada_list'),
    path('retirada/novo/', views.retirada_create, name='retirada_create'),
    path('raio-x-trade/', views.raio_x_trade, name='raio_x_trade'),
    path('aporte/editar/<int:aporte_id>/', views.aporte_edit, name='aporte_edit'),
    path('aporte/deletar/<int:aporte_id>/', views.aporte_delete, name='aporte_delete'),
    path('retirada/editar/<int:retirada_id>/', views.retirada_edit, name='retirada_edit'),
    path('retirada/deletar/<int:retirada_id>/', views.retirada_delete, name='retirada_delete'),
] 