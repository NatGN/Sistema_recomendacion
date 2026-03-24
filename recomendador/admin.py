from django.contrib import admin
from .models import Usuario, Progreso, Respuesta

# Registrar los modelos que existen
admin.site.register(Usuario)
admin.site.register(Progreso)
admin.site.register(Respuesta)