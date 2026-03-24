from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings

class Usuario(AbstractUser):
    nombre_completo = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email_verificado = models.BooleanField(default=False)
    token_activacion = models.CharField(max_length=100, blank=True, null=True)
    fecha_registro = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.username

class Progreso(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progresos')
    modulo = models.CharField(max_length=100)  # Ej: "Python Basics"
    porcentaje = models.IntegerField(default=0)  # 0-100
    ultimo_acceso = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['usuario', 'modulo']  # Un progreso por usuario y módulo
    
    def __str__(self):
        return f"{self.usuario.username} - {self.modulo}: {self.porcentaje}%"

class Respuesta(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='respuestas')
    pregunta = models.CharField(max_length=500)  # La pregunta del usuario
    respuesta = models.TextField()  # Respuesta del chatbot
    fecha = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"