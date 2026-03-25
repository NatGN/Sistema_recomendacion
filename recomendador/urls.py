from django.contrib import admin
from django.urls import path, include
from recomendador import views
from recomendador import admin_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('registro/', views.registro, name='registro'),
    path('activar/<str:token>/', views.activar_cuenta, name='activar'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Rutas del panel de administrador
    path('admin-panel/', admin_views.admin_panel, name='admin_panel'),
    path('admin-panel/usuarios/', admin_views.admin_usuarios, name='admin_usuarios'),
    path('admin-panel/usuario/<int:user_id>/toggle/', admin_views.admin_usuario_desactivar, name='admin_usuario_toggle'),
    path('admin-panel/usuario/<int:user_id>/', admin_views.admin_usuario_ver, name='admin_usuario_ver'),
    path('admin-panel/prompt/', admin_views.admin_prompt, name='admin_prompt'),
    path('admin-panel/estadisticas/', admin_views.admin_estadisticas, name='admin_estadisticas'),
    path('admin-panel/consultas/', admin_views.admin_consultas, name='admin_consultas'),
]