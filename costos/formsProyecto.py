from django import forms
from django.forms import inlineformset_factory
from .models import Proyecto, HorasEstimadasEmpleado


class ProyectoForm(forms.ModelForm):
    ganancia_porcentaje = forms.DecimalField(
        label="Ganancia (%)",
        min_value=0,
        max_value=100,
        required=True,
        initial=None,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': 1,
        })
    )

    anticipo_porcentaje = forms.DecimalField(
        label="Anticipo (%)",
        min_value=14,
        max_value=100,
        required=True,
        initial=14,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': 1,
        })
    )

    class Meta:
        model = Proyecto
        fields = ['nombre', 'cliente', 'ganancia_porcentaje', 'anticipo_porcentaje']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cliente': forms.TextInput(attrs={'class': 'form-control'}),
        }


class HorasEstimadasEmpleadoForm(forms.ModelForm):
    class Meta:
        model = HorasEstimadasEmpleado
        fields = ['empleado', 'horas_estimadas']
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select empleado-select'}),
            'horas_estimadas': forms.NumberInput(attrs={
                'class': 'form-control horas-input',
                'min': '0',
                'step': 1,
                'required': True
            }),
        }


HorasEmpleadoFormSet = inlineformset_factory(
    Proyecto,
    HorasEstimadasEmpleado,
    form=HorasEstimadasEmpleadoForm,
    extra=1,
    can_delete=True
)
