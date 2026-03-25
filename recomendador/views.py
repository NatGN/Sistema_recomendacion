import uuid
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .forms import RegistroUsuarioForm
from .models import Usuario, EstadisticasGlobales
from .admin_views import es_admin  # Importamos la función

# Create your views here.

def inicio(request):
    return render(request, 'recomendador/inicio.html')

def registro(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            # Guardar usuario pero inactivo hasta verificar email
            user = form.save(commit=False)
            user.is_active = False  # Usuario inactivo hasta verificar
            user.email_verificado = False
            user.token_activacion = str(uuid.uuid4())  # Token único para activación
            user.save()
            
            # Enviar correo de activación
            asunto = 'Activa tu cuenta en DEVPATH'
            mensaje = f"""
            Hola {user.nombre_completo},
            
            Gracias por registrarte en DEVPATH. Para activar tu cuenta y comenzar a aprender, haz clic en el siguiente enlace:
            
            {settings.ACTIVATION_URL}{user.token_activacion}
            
            Si no solicitaste este registro, ignora este mensaje.
            
            ¡Te esperamos!
            
            Equipo DEVPATH
            """
            email_origen = settings.EMAIL_HOST_USER
            email_destino = [user.email]
            
            try:
                send_mail(asunto, mensaje, email_origen, email_destino, fail_silently=False)
                messages.success(request, '¡Registro exitoso! Revisa tu correo para activar tu cuenta.')
                return redirect('login')
            except Exception as e:
                # Si falla el envío, eliminamos el usuario
                user.delete()
                messages.error(request, 'Error al enviar correo de activación. Verifica tu dirección de email.')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'recomendador/registro.html', {'form': form})

def activar_cuenta(request, token):
    try:
        usuario = Usuario.objects.get(token_activacion=token)
        usuario.is_active = True
        usuario.email_verificado = True
        usuario.token_activacion = ''
        usuario.save()
        messages.success(request, '¡Cuenta activada exitosamente! Ahora puedes iniciar sesión.')
    except Usuario.DoesNotExist:
        messages.error(request, 'Token de activación inválido o expirado.')
    
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'¡Bienvenido {user.username}!')
                
                # Redirigir según el rol del usuario
                if es_admin(user):
                    return redirect('admin_panel')
                else:
                    return redirect('dashboard')
            else:
                messages.error(request, 'Tu cuenta no ha sido activada. Revisa tu correo para activarla.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'recomendador/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('inicio')

@login_required
def dashboard(request):
    # Verificar si es admin, si es admin redirigir a su panel
    if es_admin(request.user):
        return redirect('admin_panel')
    return render(request, 'recomendador/dashboard.html', {'user': request.user})