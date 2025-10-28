from django.shortcuts import render

# Create your views here.

# libromayor/views.py

from django.shortcuts import render
from .models import Cuenta

def catalogo_cuentas_view(request):
    
    # 1. Obtenemos todas las cuentas, ordenadas por su código.
    #    Esto es crucial para que la jerarquía se muestre correctamente.
    cuentas_list = Cuenta.objects.order_by('codigo')
    
    # 2. Procesamos la lista para añadir el nivel de indentación
    cuentas_procesadas = []
    for cuenta in cuentas_list:
        
        # 3. Calculamos el "nivel" contando los puntos.
        #    '1.' -> Nivel 1 (1 punto)
        #    '1.1.' -> Nivel 2 (2 puntos)
        #    '1.1.01.' -> Nivel 3 (3 puntos)
        #    '1.1.01.01.' -> Nivel 4 (4 puntos)
        nivel = cuenta.codigo.count('.')
        
        # 4. Calculamos el padding (espacio a la izquierda)
        #    Restamos 1 para que el Nivel 1 no tenga padding.
        #    Multiplicamos por 25px (puedes ajustar este valor).
        padding_px = nivel * 15
        
        # 5. Determinamos si es una "cuenta de grupo" (para el estilo)
        #    Asumimos que las cuentas de nivel 1 y 2 son grupos (como en tu imagen)
        es_grupo = (nivel <= 2)
        
        cuentas_procesadas.append({
            'cuenta': cuenta,
            'padding': padding_px,
            'es_grupo': es_grupo
        })

    # 6. Enviamos los datos procesados a la plantilla
    context = {
        'cuentas_procesadas': cuentas_procesadas
    }
    
    # Asegúrate de que el nombre de la plantilla sea correcto
    return render(request, 'catalogo_cuentas.html', context)