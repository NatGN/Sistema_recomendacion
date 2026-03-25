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
    is_admin = models.BooleanField(default=False)  # Campo para identificar admin
    
    def __str__(self):
        return self.username
    
    @property
    def total_consultas(self):
        """Total de consultas realizadas por el usuario"""
        return self.respuestas.count()
    
    @property
    def progreso_promedio(self):
        """Promedio de progreso en todos los módulos"""
        progresos = self.progresos.all()
        if progresos.exists():
            total = sum(p.porcentaje for p in progresos)
            return total // progresos.count()
        return 0

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

class PromptConfig(models.Model):
    """Modelo para guardar la configuración del prompt que se usará con la API"""
    nombre = models.CharField(max_length=100, default='default')  # Identificador del prompt
    prompt_texto = models.TextField(default='Eres un asistente educativo especializado en programación. Ayuda al usuario a aprender de forma clara y didáctica.')
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    ultima_actualizacion_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='prompts_editados'
    )
    
    def __str__(self):
        return f"Prompt: {self.nombre} - Última actualización: {self.fecha_actualizacion.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        verbose_name = "Configuración de Prompt"
        verbose_name_plural = "Configuraciones de Prompt"

class EstadisticasGlobales(models.Model):
    """Modelo para estadísticas globales del sistema"""
    total_consultas = models.IntegerField(default=0)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Total consultas: {self.total_consultas}"
    
    class Meta:
        verbose_name = "Estadística Global"
        verbose_name_plural = "Estadísticas Globales"