from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from .models import Usuario, Respuesta, PromptConfig, EstadisticasGlobales, Progreso

def es_admin(user):
    """Verifica si el usuario es administrador"""
    return user.is_authenticated and (user.is_staff or user.is_superuser or getattr(user, 'is_admin', False))

@login_required
@user_passes_test(es_admin)
def admin_panel(request):
    """Panel principal del administrador"""
    usuarios = Usuario.objects.all().order_by('-date_joined')
    total_usuarios = usuarios.count()
    usuarios_activos = usuarios.filter(is_active=True).count()
    
    # Obtener estadísticas globales o crearlas si no existen
    estadisticas, created = EstadisticasGlobales.objects.get_or_create(id=1)
    
    # Actualizar total de consultas desde Respuesta
    estadisticas.total_consultas = Respuesta.objects.count()
    estadisticas.save()
    
    context = {
        'usuarios': usuarios,
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'total_consultas': estadisticas.total_consultas,
        'seccion_activa': 'dashboard'
    }
    return render(request, 'recomendador/admin_panel.html', context)

@login_required
@user_passes_test(es_admin)
def admin_usuarios(request):
    """Gestión de usuarios"""
    usuarios = Usuario.objects.all().order_by('-date_joined')
    
    # Para cada usuario, calcular estadísticas adicionales
    for usuario in usuarios:
        usuario.total_consultas = usuario.respuestas.count()
        usuario.progreso_total = usuario.progreso_promedio
    
    context = {
        'usuarios': usuarios,
        'seccion_activa': 'usuarios'
    }
    return render(request, 'recomendador/admin_usuarios.html', context)

@login_required
@user_passes_test(es_admin)
def admin_usuario_desactivar(request, user_id):
    """Desactivar/Activar usuario"""
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, id=user_id)
        # No permitir desactivar al propio admin
        if usuario.id == request.user.id:
            messages.error(request, 'No puedes desactivar tu propia cuenta.')
            return redirect('admin_usuarios')
        
        usuario.is_active = not usuario.is_active
        usuario.save()
        
        estado = "activado" if usuario.is_active else "desactivado"
        messages.success(request, f'Usuario {usuario.username} {estado} correctamente.')
    
    return redirect('admin_usuarios')

@login_required
@user_passes_test(es_admin)
def admin_usuario_ver(request, user_id):
    """Ver detalles de un usuario específico"""
    usuario = get_object_or_404(Usuario, id=user_id)
    consultas = usuario.respuestas.all().order_by('-fecha')[:20]  # Últimas 20 consultas
    progresos = usuario.progresos.all()
    
    context = {
        'usuario': usuario,
        'consultas': consultas,
        'progresos': progresos,
        'total_consultas': usuario.respuestas.count(),
        'seccion_activa': 'usuarios'
    }
    return render(request, 'recomendador/admin_usuario_detalle.html', context)

@login_required
@user_passes_test(es_admin)
def admin_prompt(request):
    """Editor del prompt general"""
    # Obtener el prompt principal o crearlo si no existe
    prompt_config, created = PromptConfig.objects.get_or_create(
        nombre='default',
        defaults={
            'prompt_texto': 'Eres un asistente educativo especializado en programación llamado DEVPATH. Tu misión es ayudar a los estudiantes a aprender programación de forma clara, didáctica y personalizada. Responde con ejemplos prácticos, explicaciones paso a paso y fomenta el pensamiento crítico. Adapta tu lenguaje al nivel del usuario (principiante, intermedio o avanzado). Siempre sé amable, paciente y motivador.'
        }
    )
    
    if request.method == 'POST':
        nuevo_prompt = request.POST.get('prompt_texto', '')
        if nuevo_prompt:
            prompt_config.prompt_texto = nuevo_prompt
            prompt_config.ultima_actualizacion_por = request.user
            prompt_config.save()
            messages.success(request, 'El prompt ha sido actualizado exitosamente.')
            return redirect('admin_prompt')
    
    context = {
        'prompt': prompt_config,
        'seccion_activa': 'prompt'
    }
    return render(request, 'recomendador/admin_prompt.html', context)

@login_required
@user_passes_test(es_admin)
def admin_estadisticas(request):
    """Panel de estadísticas detalladas"""
    # Estadísticas globales
    total_usuarios = Usuario.objects.count()
    usuarios_activos = Usuario.objects.filter(is_active=True).count()
    usuarios_inactivos = total_usuarios - usuarios_activos
    
    total_consultas = Respuesta.objects.count()
    consultas_hoy = Respuesta.objects.filter(fecha__date=timezone.now().date()).count()
    consultas_semana = Respuesta.objects.filter(fecha__gte=timezone.now() - timezone.timedelta(days=7)).count()
    
    # Progreso promedio general
    todos_progresos = Progreso.objects.all()
    if todos_progresos.exists():
        progreso_promedio = sum(p.porcentaje for p in todos_progresos) // todos_progresos.count()
    else:
        progreso_promedio = 0
    
    # Top usuarios con más consultas
    top_usuarios = Usuario.objects.annotate(
        num_consultas=Count('respuestas')
    ).order_by('-num_consultas')[:5]
    
    context = {
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'usuarios_inactivos': usuarios_inactivos,
        'total_consultas': total_consultas,
        'consultas_hoy': consultas_hoy,
        'consultas_semana': consultas_semana,
        'progreso_promedio': progreso_promedio,
        'top_usuarios': top_usuarios,
        'seccion_activa': 'estadisticas'
    }
    return render(request, 'recomendador/admin_estadisticas.html', context)

@login_required
@user_passes_test(es_admin)
def admin_consultas(request):
    """Ver todas las consultas del sistema"""
    consultas = Respuesta.objects.all().select_related('usuario').order_by('-fecha')
    
    context = {
        'consultas': consultas,
        'total_consultas': consultas.count(),
        'seccion_activa': 'consultas'
    }
    return render(request, 'recomendador/admin_consultas.html', context)