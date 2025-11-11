from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .models import Proyecto
from .forms import ProyectoForm

from django.views.decorators.http import require_POST

def lista_proyectos_view(request):
    proyectos = Proyecto.objects.all()
    return render(request, 'proyectos.html', {'proyectos': proyectos})

def crear_proyecto_view(request):
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save()
            messages.success(request, f'Proyecto "{proyecto.nombre}" creado exitosamente. Procede a calcular costos.')
            return redirect(reverse('gestion_ucp') + f'?proyecto_id={proyecto.id}')
    else:
        form = ProyectoForm()
    
    return render(request, 'form_proyecto.html', {
        'form': form,
        'accion': 'Crear'
    })

@require_POST
def guardar_costo_venta_view(request):
    """
    Guarda en el proyecto los valores calculados desde costo_venta:
    - precio_venta  <= saleCost
    - costo_total_estimado <= unitCost
    Requiere proyecto_id en POST.
    """
    proyecto_id = request.POST.get('proyecto_id')
    if not proyecto_id:
        messages.error(request, 'No se recibió el identificador del proyecto.')
        return redirect('lista_proyectos')

    proyecto = get_object_or_404(Proyecto, pk=proyecto_id)

    # Leer valores del formulario
    sale_cost_str = request.POST.get('saleCost', '0')
    unit_cost_str = request.POST.get('unitCost', '0')

    try:
        from decimal import Decimal
        proyecto.precio_venta = Decimal(sale_cost_str or '0')
        proyecto.costo_total_estimado = Decimal(unit_cost_str or '0')
        proyecto.save()
        messages.success(request, f'Se guardaron los costos del proyecto "{proyecto.nombre}".')
    except Exception as e:
        messages.error(request, f'No se pudieron guardar los costos: {e}')

    return redirect('lista_proyectos')
def editar_proyecto_view(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    
    if request.method == 'POST':
        form = ProyectoForm(request.POST, instance=proyecto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proyecto actualizado exitosamente.')
            return redirect('lista_proyectos')
    else:
        form = ProyectoForm(instance=proyecto)
    
    return render(request, 'form_proyecto.html', {
        'form': form,
        'accion': 'Editar'
    })

def eliminar_proyecto_view(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    
    if request.method == 'POST':
        proyecto.delete()
        messages.success(request, 'Proyecto eliminado exitosamente.')
        return redirect('lista_proyectos')
    
    return redirect('lista_proyectos')
