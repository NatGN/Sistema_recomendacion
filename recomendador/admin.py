from django.contrib import admin
from .models import Usuario, Progreso, Respuesta, PromptConfig, EstadisticasGlobales

admin.site.register(Usuario)
admin.site.register(Progreso)
admin.site.register(Respuesta)
admin.site.register(PromptConfig)
admin.site.register(EstadisticasGlobales)