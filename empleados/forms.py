from django import forms
from .models import Empleado

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        # Excluir los campos calculados que tienen editable=False o que se manejan en save()
        exclude = [
            'costo_real_hora_ajustado',
            'salario_bruto_mensual_calculado',
            'aporte_patronal_isss_mensual',
            'aporte_patronal_afp_mensual',
            'deduccion_isss_mensual',
            'deduccion_afp_mensual',
            'total_deducciones_mensual',
            'pago_liquido_mensual',
        ]

    # Puedes agregar validaciones adicionales aquí si lo necesitas