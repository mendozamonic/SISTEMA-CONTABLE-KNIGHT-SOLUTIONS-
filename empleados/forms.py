from django import forms
from .models import Empleado

class EmpleadoForm(forms.ModelForm):
    """
    Formulario para el registro de nuevos empleados.
    Incluye solo los campos de entrada de datos, excluyendo los campos calculados.
    """
    class Meta:
        model = Empleado
        
        # 1. CAMPOS DE ENTRADA (INPUT FIELDS)
        fields = [
            'nombre',
            'cargo',
            'salario_diario',
            'dias_laborados_semana',
            'horas_laboradas_diarias',
            'dias_vacaciones_anual',
            'recargo_vacaciones',
            'dias_aguinaldo_anual',
            'eficiencia',
        ]
        
        # 2. EXCLUSIÓN DE CAMPOS CALCULADOS
        # Estos campos son calculados en el método save() del modelo y NO deben ser editables.
        # Although they are excluded by default if not listed in 'fields', 
        # listing them here provides clear documentation and prevents accidental inclusion.
        # If 'fields' is defined, 'exclude' is not strictly necessary but helps clarify intent.
        exclude = [
            'costo_real_hora_ajustado',
            'salario_bruto_mensual_calculado',
            'aporte_patronal_isss_mensual',
            'aporte_patronal_afp_mensual',
            'deduccion_isss_mensual',
            'deduccion_afp_mensual',
            'deduccion_renta_mensual',
            'total_deducciones_mensual',
            'pago_liquido_mensual',
             'dias_laborados_semana',
            'horas_laboradas_diarias',
            'dias_vacaciones_anual',
            'recargo_vacaciones',
            'dias_aguinaldo_anual',
            'eficiencia',
        ]