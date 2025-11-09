# empleados/views.py
from django.shortcuts import render, redirect # Importa redirect para la redirección
from .models import Empleado 
from .forms import EmpleadoForm # Importa el formulario que acabas de crear

# (Mantener la función lista_empleados tal como la definimos antes)
def tabla_empleados(request):
    empleados_qs = Empleado.objects.all().order_by('nombre')
    contexto = {'empleados': empleados_qs}
    # **IMPORTANTE:** El campo costo_real_ajustado de tu HTML debe cambiarse
    # al nombre real del modelo: costo_real_hora_ajustado
    return render(request, 'empleados/tabla_empleados.html', contexto)


def registro_empleado(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            # When .save() is called, the Empleado model's save method
            # automatically runs all the payroll calculations before committing to the DB.
            form.save() 
            return redirect('empleados:tabla_empleados') # Redirect to the data display view
    else:
        form = EmpleadoForm()
        
    return render(request, 'empleados/registrar_empleado.html', {'form': form})

# Don't forget to import this view and define a URL pattern for it!