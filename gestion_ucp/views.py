from django.shortcuts import render, redirect
from django.contrib import messages
from .models import EstimacionUCP

def ucp_view(request):
    """
    Muestra la página de cálculo del método UCP y las estimaciones guardadas.
    """
    estimaciones = EstimacionUCP.objects.all().order_by('-creado_en')
    context = {'estimaciones': estimaciones}
    return render(request, 'gestion_ucp.html', context)


def guardar_estimacion_ucp(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        horas_totales = request.POST.get('horas_totales')

        if not nombre or not horas_totales:
            messages.error(request, 'Faltan datos para guardar la estimación.')
            return redirect('ucp_view')

        try:
            horas_totales = round(float(horas_totales))  # 👈 redondea al entero más cercano
        except ValueError:
            messages.error(request, 'El valor de horas totales no es válido.')
            return redirect('ucp_view')

        EstimacionUCP.objects.create(
            nombre=nombre,
            horas_totales=horas_totales,
            usado=False
        )

        messages.success(request, f'Estimación "{nombre}" guardada correctamente ({horas_totales} horas).')
        return redirect('ucp_view')
