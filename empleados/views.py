# empleados/views.py
from django.shortcuts import render, redirect # Importa redirect para la redirección
from .models import Empleado 
from .forms import EmpleadoForm # Importa el formulario que acabas de crear

# (Mantener la función lista_empleados tal como la definimos antes)
def lista_empleados(request):
    empleados_qs = Empleado.objects.all().order_by('nombre')
    contexto = {'empleados': empleados_qs}
    # **IMPORTANTE:** El campo costo_real_ajustado de tu HTML debe cambiarse
    # al nombre real del modelo: costo_real_hora_ajustado
    return render(request, 'empleados/tabla_empleados.html', contexto)


def registrar_empleado(request):
    """Maneja la creación de nuevos empleados."""
    if request.method == 'POST':
        # 1. Cuando se envía el formulario
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            try:
                empleado = form.save() # Guarda y ejecuta automáticamente el método save() del modelo
                return redirect('empleados:lista_empleados') # Redirige a la lista después del registro
            except Exception as e:
                # Manejo de errores complejos del save()
                contexto = {'form': form, 'error_message': f"Error al guardar: {e}"}
                return render(request, 'empleados/registrar_empleado.html', contexto)
    else:
        # 2. Cuando se visita la página por primera vez (GET)
        form = EmpleadoForm()
        
    contexto = {'form': form, 'page_title': 'Registrar Nuevo Empleado'}
    return render(request, 'empleados/registrar_empleado.html', contexto)