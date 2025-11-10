from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from libromayor.models import ParametrosGlobales


class Empleado(models.Model):
    """
    Información del empleado. Calcula y guarda automáticamente 
    costo por hora con y sin eficiencia, y datos de planilla mensual.
    """

    # --- DATOS BÁSICOS ---
    nombre = models.CharField(max_length=255)
    cargo = models.CharField(max_length=150)
    salario_diario = models.DecimalField(max_digits=10, decimal_places=2, help_text="Salario base por día trabajado")
    
    # --- PARÁMETROS ESPECÍFICOS DEL EMPLEADO ---
    dias_laborados_semana = models.IntegerField(help_text="Días que labora a la semana (ej: 5)", null=True, blank=True)
    horas_laboradas_diarias = models.IntegerField(help_text="Horas estándar por día (ej: 8)", null=True, blank=True)
    dias_vacaciones_anual = models.IntegerField(help_text="Días de vacaciones pagadas al año", null=True, blank=True)
    recargo_vacaciones = models.DecimalField(max_digits=5, decimal_places=2, help_text="Recargo sobre vacaciones (ej: 0.30)", null=True, blank=True)
    dias_aguinaldo_anual = models.IntegerField(help_text="Días de aguinaldo", null=True, blank=True)
    eficiencia = models.DecimalField(max_digits=5, decimal_places=2, help_text="Factor de eficiencia (ej: 0.85)", null=True, blank=True)
    
    # --- RESULTADOS CALCULADOS (Se guardan automáticamente) ---
    costo_real_hora_sin_eficiencia = models.DecimalField(
        max_digits=10, decimal_places=4,
        help_text="Costo real por hora sin eficiencia (calculado)",
        blank=True, null=True, editable=False
    )
    costo_real_hora_ajustado = models.DecimalField(
        max_digits=10, decimal_places=4, 
        help_text="Costo real por hora con eficiencia (calculado)", 
        blank=True, null=True, editable=False
    )
    salario_bruto_mensual_calculado = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Salario Bruto Mensual (calculado)",
        blank=True, null=True, editable=False
    )
    # --- APORTES PATRONALES MENSUALES ---
    aporte_patronal_isss_mensual = models.DecimalField(
        max_digits=10, decimal_places=2, 
        help_text="Aporte patronal mensual ISSS (calculado)", 
        blank=True, null=True, editable=False
    )
    aporte_patronal_afp_mensual = models.DecimalField(
        max_digits=10, decimal_places=2, 
        help_text="Aporte patronal mensual AFP (calculado)", 
        blank=True, null=True, editable=False
    )
    # --- DEDUCCIONES EMPLEADO MENSUALES ---
    deduccion_isss_mensual = models.DecimalField(
        max_digits=10, decimal_places=2, 
        help_text="Deducción mensual ISSS empleado (calculado)", 
        blank=True, null=True, editable=False
    )
    deduccion_afp_mensual = models.DecimalField(
        max_digits=10, decimal_places=2, 
        help_text="Deducción mensual AFP empleado (calculado)", 
        blank=True, null=True, editable=False
    )
    total_deducciones_mensual = models.DecimalField(
        max_digits=10, decimal_places=2, 
        help_text="Total deducciones mensuales (calculado)", 
        blank=True, null=True, editable=False
    )
    pago_liquido_mensual = models.DecimalField(
        max_digits=10, decimal_places=2, 
        help_text="Pago líquido mensual estimado (calculado)", 
        blank=True, null=True, editable=False
    )

    def __str__(self):
        return self.nombre

    # --- Funciones auxiliares ---
    def get_parametros_globales(self):
        try:
            return ParametrosGlobales.objects.get()
        except ParametrosGlobales.DoesNotExist:
            raise ValidationError("No se han configurado los Parámetros Globales.")
            
    def set_defaults_from_globales(self):
        params = self.get_parametros_globales()
        if not params:
            return 

        if self.dias_laborados_semana is None: 
            self.dias_laborados_semana = params.dias_laborados_semana
        if self.horas_laboradas_diarias is None: 
            self.horas_laboradas_diarias = params.horas_laboradas_diarias
        if self.recargo_vacaciones is None: 
            self.recargo_vacaciones = params.recargo_vacaciones
        if self.eficiencia is None: 
            self.eficiencia = params.eficiencia_base

    # --- Guardado automático ---
    def save(self, *args, **kwargs):
        # Intentar llenar defaults si es nuevo
        if self.pk is None:
            try:
                self.set_defaults_from_globales()
            except ValidationError as e:
                print(f"Error al guardar empleado {self.nombre}: {e}")
                self._set_calculated_fields_to_none()
                super().save(*args, **kwargs) 
                return 

        try:
            params = self.get_parametros_globales()

            # 1️⃣ Calcular costos reales
            costos = self._calcular_costo_real(params)
            if costos:
                self.costo_real_hora_sin_eficiencia = costos['sin']
                self.costo_real_hora_ajustado = costos['con']
            else:
                self.costo_real_hora_sin_eficiencia = None
                self.costo_real_hora_ajustado = None

            # 2️⃣ Calcular planilla mensual
            planilla_data = self._calcular_datos_planilla_mensual(params)
            if planilla_data:
                self.salario_bruto_mensual_calculado = planilla_data['bruto']
                self.aporte_patronal_isss_mensual = planilla_data['aporte_patronal_isss']
                self.aporte_patronal_afp_mensual = planilla_data['aporte_patronal_afp']
                self.deduccion_isss_mensual = planilla_data['deduccion_isss']
                self.deduccion_afp_mensual = planilla_data['deduccion_afp']
                self.total_deducciones_mensual = planilla_data['total_deducciones']
                self.pago_liquido_mensual = planilla_data['pago_liquido']
            else:
                self._set_calculated_fields_to_none()

        except Exception as e:
            print(f"Error al calcular empleado {self.nombre}: {e}")
            self._set_calculated_fields_to_none()

        super().save(*args, **kwargs)

    def _set_calculated_fields_to_none(self):
        """Limpia los campos calculados en caso de error."""
        self.costo_real_hora_sin_eficiencia = None
        self.costo_real_hora_ajustado = None
        self.salario_bruto_mensual_calculado = None
        self.aporte_patronal_isss_mensual = None
        self.aporte_patronal_afp_mensual = None
        self.deduccion_isss_mensual = None
        self.deduccion_afp_mensual = None
        self.total_deducciones_mensual = None
        self.pago_liquido_mensual = None

    # --- Cálculos internos ---
    def _calcular_costo_real(self, params):
        """
        Calcula el costo real por hora (con y sin eficiencia).
        Retorna ambos valores en un diccionario.
        """
        required_fields_empleado = [
            self.salario_diario, self.dias_vacaciones_anual, self.recargo_vacaciones,
            self.dias_aguinaldo_anual, self.dias_laborados_semana, 
            self.horas_laboradas_diarias, self.eficiencia
        ]
        if None in required_fields_empleado: 
            return None
        required_params = [params.patronal_seguro_social, params.patronal_afp]
        if None in required_params: 
            return None
        
        # --- Cálculos ---
        salario_septimo = self.salario_diario * 7
        costo_anual_vac = self.salario_diario * self.dias_vacaciones_anual * (1 + self.recargo_vacaciones) # type: ignore
        prov_sem_vac = (costo_anual_vac / Decimal('365')) * 7
        costo_anual_agui = self.salario_diario * self.dias_aguinaldo_anual # type: ignore
        prov_sem_agui = (costo_anual_agui / Decimal('365')) * 7

        base_cotizacion = salario_septimo + prov_sem_vac
        costo_sem_isss = base_cotizacion * params.patronal_seguro_social 
        costo_sem_afp = base_cotizacion * params.patronal_afp

        costo_real_sem = (
            salario_septimo + prov_sem_vac + prov_sem_agui +
            costo_sem_isss + costo_sem_afp
        )

        if self.dias_laborados_semana == 0 or self.horas_laboradas_diarias == 0:
            return {'sin': Decimal('0.00'), 'con': Decimal('0.00')}
        
        horas_semana = Decimal(self.dias_laborados_semana) * Decimal(self.horas_laboradas_diarias) # type: ignore
        costo_sin_ef = costo_real_sem / horas_semana
        costo_con_ef = costo_sin_ef / self.eficiencia if self.eficiencia else costo_sin_ef

        return {
            'sin': round(costo_sin_ef, 4),
            'con': round(costo_con_ef, 4)
        }

    def _calcular_datos_planilla_mensual(self, params):
        """Calcula datos de planilla mensual (bruto, deducciones y líquido)."""
        if self.salario_diario is None:
            return None

        required_params_planilla = [
            params.patronal_seguro_social, params.patronal_afp,
            params.empleado_seguro_social, params.empleado_afp
        ]
        if None in required_params_planilla:
            return None

        salario_bruto_mensual = self.salario_diario * Decimal('30')
        
        base_isss_patronal = min(salario_bruto_mensual, Decimal('1000.00')) 
        aporte_patronal_isss = base_isss_patronal * params.patronal_seguro_social
        aporte_patronal_afp = salario_bruto_mensual * params.patronal_afp
        
        base_isss_empleado = min(salario_bruto_mensual, Decimal('1000.00')) 
        deduccion_isss = base_isss_empleado * params.empleado_seguro_social
        deduccion_afp = salario_bruto_mensual * params.empleado_afp
        
        total_deducciones = deduccion_isss + deduccion_afp
        pago_liquido = salario_bruto_mensual - total_deducciones
        
        return {
            'bruto': round(salario_bruto_mensual, 2),
            'aporte_patronal_isss': round(aporte_patronal_isss, 2),
            'aporte_patronal_afp': round(aporte_patronal_afp, 2),
            'deduccion_isss': round(deduccion_isss, 2),
            'deduccion_afp': round(deduccion_afp, 2),
            'total_deducciones': round(total_deducciones, 2),
            'pago_liquido': round(pago_liquido, 2)
        }
