from django.contrib import admin
from django.urls import path, include
from recomendador import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('registro/', views.registro, name='registro'),
    path('activar/<str:token>/', views.activar_cuenta, name='activar'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
]