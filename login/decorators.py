from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

def cliente_required(view_func):
    """
    Asegura que el usuario pertenece al grupo 'clientes'.
    """
    @login_required  # Asegura que el usuario esté autenticado
    def _wrapped_view(request, *args, **kwargs):
        # Verificar si el usuario pertenece al grupo "clientes"
        if request.user.groups.filter(name='clientes').exists():
            # Lógica adicional para clientes
            if not request.user.is_active:
                # Redirigir o mostrar un mensaje si el usuario no está activo
                return HttpResponseForbidden("Tu cuenta está inactiva. Contacta al soporte.")
            
            # Opcional: Redireccionar si la cuenta de cliente no está completa
            if not request.user.email:
                return redirect('actualizar_perfil')  # Cambia a la vista correspondiente

            # Permitir el acceso si cumple con los requisitos
            return view_func(request, *args, **kwargs)
        else:
            # Denegar el acceso si no es cliente
            return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
    return _wrapped_view