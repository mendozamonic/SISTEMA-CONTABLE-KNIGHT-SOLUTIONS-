from django.shortcuts import render
from django.contrib import messages

# Create your views here.

def gestion_ucp_view(request):
    """
    Vista principal para la gestión de UCP (Unidad de Costo de Producción)
    """
    context = {
        'titulo': 'Gestión UCP - Unidad de Costo de Producción',
    }
    
    return render(request, 'gestion_ucp.html', context)
