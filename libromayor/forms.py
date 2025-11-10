# contabilidad/forms.py
from django import forms
from django.forms import formset_factory
from .models import AsientoContable, DetalleAsiento, Cuenta, PeriodoContable , EstimacionCostoIndirectoGlobal
from decimal import Decimal
import calendar
from django.core.exceptions import ValidationError
from .models import ParametrosGlobales

class AsientoContableForm(forms.ModelForm):

    # Formulario para registrar un Asiento Contable.
    # - El período se autoselecciona y se bloquea (único activo).
    # - La fecha solo puede estar dentro del período activo.
    # - El tipo de asiento se elimina (va en la descripción).

    class Meta:
        model = AsientoContable
        fields = [
            'periodo', 
            'fecha', 
            'concepto', 
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'concepto': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔹 Buscar el único período contable activo
        periodo_activo = PeriodoContable.objects.filter(cerrado=False).first()

        if periodo_activo:
            # Solo mostrar el período activo y bloquearlo
            self.fields['periodo'].queryset = PeriodoContable.objects.filter(pk=periodo_activo.pk) # type: ignore
            self.fields['periodo'].initial = periodo_activo
            self.fields['periodo'].disabled = True
            self.periodo_activo = periodo_activo

            # Limitar fechas dentro del período activo
            self.fields['fecha'].widget.attrs['min'] = periodo_activo.inicio.isoformat()
            self.fields['fecha'].widget.attrs['max'] = periodo_activo.fin.isoformat()
        else:
            # Si no hay período abierto, desactivar el formulario
            self.fields['periodo'] = forms.ModelChoiceField(
                queryset=PeriodoContable.objects.none(),
                label="Período Contable",
                widget=forms.Select(attrs={'class': 'form-select'}),
            )
            self.fields['fecha'].widget.attrs['readonly'] = True
            self.fields['concepto'].widget.attrs['readonly'] = True

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get("fecha")

        # Validar que la fecha esté dentro del período activo
        if hasattr(self, 'periodo_activo') and fecha:
            if not (self.periodo_activo.inicio <= fecha <= self.periodo_activo.fin):
                raise ValidationError(
                    f"La fecha {fecha} está fuera del rango del período activo "
                    f"({self.periodo_activo.inicio} al {self.periodo_activo.fin})."
                )

        return cleaned_data


class DetalleAsientoForm(forms.Form):
    """
    Formulario para una LÍNEA de detalle (Debe o Haber).
    """

    TIPO_OPCIONES = [
        ('ACT', 'Activo'),
        ('PAS', 'Pasivo'),
        ('PAT', 'Patrimonio'),
        ('ING', 'Ingreso'),
        ('GAS', 'Gasto'),
        ('COS', 'Costo'),
    ]

    tipo_cuenta = forms.ChoiceField(
        choices=[('', '--- Seleccione tipo ---')] + TIPO_OPCIONES,
        label="Tipo de cuenta",
        widget=forms.Select(attrs={
            'class': 'form-select tipo-cuenta-select',
            'id': 'tipo-cuenta-select'
        })
    )

    cuenta = forms.ModelChoiceField(
        queryset=Cuenta.objects.none(),
        label="Cuenta Contable",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'cuenta-select'})
    )
    
    tipo_monto = forms.ChoiceField(
        choices=[('Debe', 'Debe'), ('Haber', 'Haber')],
        label="Tipo de Monto",
        widget=forms.Select(attrs={'class': 'form-select tipo-monto-select'})
    )
    
    monto = forms.DecimalField(
        label="Monto",
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control monto-input',
            'step': '0.01',
            'placeholder': 'Digite el monto'
        })
    )

    # ✅ Este es el __init__ que faltaba en el lugar correcto
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        data = self.data or self.initial

        tipo_cuenta = data.get(self.add_prefix('tipo_cuenta'))
        if tipo_cuenta:
            self.fields['cuenta'].queryset = Cuenta.objects.filter( # type: ignore
                tipo_cuenta=tipo_cuenta,
                es_imputable=True
            ).order_by('codigo')
        else:
            self.fields['cuenta'].queryset = Cuenta.objects.none() # type: ignore


# Creamos un Formset basado en DetalleAsientoForm
DetalleAsientoFormSet = formset_factory(
    DetalleAsientoForm, 
    min_num=1,
    validate_min=True 
)



class PeriodoContableForm(forms.ModelForm):
    class Meta:
        model = PeriodoContable
        fields = ['nombre', 'inicio', 'fin']
        widgets = {
            'inicio': forms.DateInput(attrs={'type': 'date'}),
            'fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si es edición → deshabilitamos las fechas
        if self.instance.pk:
            self.fields['inicio'].disabled = True
            self.fields['fin'].disabled = True
    
    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get('inicio')
        fin = cleaned_data.get('fin')

        # Si faltan datos, no validar aún
        if not inicio or not fin:
            return cleaned_data

        # --- Validaciones ya existentes ---
        if fin < inicio:
            self.add_error('fin', 'La fecha de fin no puede ser anterior a la fecha de inicio.')

        import calendar
        if inicio.day != 1:
            self.add_error('inicio', 'La fecha de inicio debe ser el primer día del mes (día 1).')

        num_dias_mes = calendar.monthrange(inicio.year, inicio.month)[1]
        if (fin.year != inicio.year or fin.month != inicio.month or fin.day != num_dias_mes):
            self.add_error('fin', f'La fecha de fin debe ser el último día del mes ({num_dias_mes}/{inicio.month}/{inicio.year}).')

        # --- Validar solapamiento ---
        qs = PeriodoContable.objects.filter(inicio__lte=fin, fin__gte=inicio)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Las fechas de este período se solapan con otro existente.')

        # --- ✅ Nueva validación: no permitir períodos anteriores al más reciente ---
        ultimo_periodo = PeriodoContable.objects.order_by('-fin').first()
        if ultimo_periodo:
            if fin <= ultimo_periodo.fin:
                raise forms.ValidationError(
                    f'No puede crear un período anterior o igual al existente ({ultimo_periodo.nombre}: {ultimo_periodo.inicio} → {ultimo_periodo.fin}).'
                )

        # --- Validar que no haya otro período abierto ---
        if not self.instance.pk and PeriodoContable.objects.filter(cerrado=False).exists():
            raise forms.ValidationError('Ya existe un período contable abierto. Cierre el actual antes de crear uno nuevo.')

        return cleaned_data


class ParametrosGlobalesForm(forms.ModelForm):
    class Meta:
        model = ParametrosGlobales
        exclude = ['tasa_gastos_indirectos_por_hora']

class EstimacionCostoIndirectoGlobalForm(forms.ModelForm):
    class Meta:
        model = EstimacionCostoIndirectoGlobal
        fields = ['nombre', 'descripcion', 'monto_estimado_mensual']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'monto_estimado_mensual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }