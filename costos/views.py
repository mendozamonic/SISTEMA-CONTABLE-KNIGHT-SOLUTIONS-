from django.shortcuts import render

# Create your views here.

def costos_indirectos_view(request):
    """
    Vista para la calculadora de costos indirectos del proyecto
    """
    context = {
        'titulo': 'Calculadora de Costos Indirectos',
    }
    
    return render(request, 'costo_indirecto.html', context)
