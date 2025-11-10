from django import forms
from .models import Empleado, ParametrosGlobales

class EmpleadoForm(forms.ModelForm):
    CARGOS = [
        ('Gerente General', 'Gerente General'),
        ('Desarrollador Back-End', 'Desarrollador Back-End'),
        ('Desarrollador Front-End', 'Desarrollador Front-End'),
        ('Programador Full-Stack Jr.', 'Programador Full-Stack Jr.'),
        ('QA Tester / Control Calidad', 'QA Tester / Control Calidad'),
        ('Diseñador UX/UI', 'Diseñador UX/UI'),
        ('Contador', 'Contador'),
        ('Recursos Humanos / Reclutamiento', 'Recursos Humanos / Reclutamiento'),
        ('Marketing', 'Marketing'),
        ('Secretaria', 'Secretaria'),
        ('Soporte Técnico', 'Soporte Técnico'),
        ('Servicio al Cliente', 'Servicio al Cliente'),
    ]

    cargo = forms.ChoiceField(
        choices=CARGOS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Empleado
        fields = [
            'nombre', 'cargo', 'salario_diario',
            'dias_laborados_semana', 'horas_laboradas_diarias',
            'dias_vacaciones_anual', 'dias_aguinaldo_anual',
            'recargo_vacaciones', 'eficiencia'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'salario_diario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'dias_laborados_semana': forms.NumberInput(attrs={'class': 'form-control'}),
            'horas_laboradas_diarias': forms.NumberInput(attrs={'class': 'form-control'}),
            'dias_vacaciones_anual': forms.NumberInput(attrs={'class': 'form-control'}),
            'dias_aguinaldo_anual': forms.NumberInput(attrs={'class': 'form-control'}),
            'recargo_vacaciones': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'eficiencia': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            p = ParametrosGlobales.objects.first()
            if p:
                self.fields['dias_laborados_semana'].initial = p.dias_laborados_semana
                self.fields['horas_laboradas_diarias'].initial = p.horas_laboradas_diarias
                self.fields['recargo_vacaciones'].initial = p.recargo_vacaciones
                self.fields['eficiencia'].initial = p.eficiencia_base
                self.fields['dias_vacaciones_anual'].initial = 15
                self.fields['dias_aguinaldo_anual'].initial = 15
        except:
            pass
