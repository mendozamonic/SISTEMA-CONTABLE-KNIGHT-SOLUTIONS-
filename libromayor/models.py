from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
import calendar
from django.db.models import Sum


# --- PERÍODO CONTABLE ---
from django.core.exceptions import ValidationError
import calendar

class PeriodoContable(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    inicio = models.DateField()
    fin = models.DateField()
    cerrado = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

    def clean(self):
        super().clean()

        # ✅ Verificar que ambas fechas existan antes de comparar
        if not self.inicio or not self.fin:
            return  # Si faltan datos, no validar aún (el form lo manejará)

        # Validar orden de fechas
        if self.fin < self.inicio:
            raise ValidationError("La fecha de fin no puede ser anterior a la de inicio.")

        # Validar que inicio sea el primer día del mes
        if self.inicio.day != 1:
            raise ValidationError("La fecha de inicio debe ser el primer día del mes (día 1).")

        # Validar que fin sea el último día del mismo mes
        num_dias_mes = calendar.monthrange(self.inicio.year, self.inicio.month)[1]
        if (
            self.fin.year != self.inicio.year
            or self.fin.month != self.inicio.month
            or self.fin.day != num_dias_mes
        ):
            raise ValidationError(
                f"La fecha de fin debe ser el último día del mes ({num_dias_mes}/{self.inicio.month}/{self.inicio.year})."
            )

        # Validar solapamiento con otros períodos
        qs = PeriodoContable.objects.filter(inicio__lte=self.fin, fin__gte=self.inicio)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError("Las fechas de este período se solapan con otro existente.")


# --- CATÁLOGO DE CUENTAS ---
class Cuenta(models.Model):
    class TipoCuenta(models.TextChoices):
        ACTIVO = 'ACT', 'Activo'
        PASIVO = 'PAS', 'Pasivo'
        PATRIMONIO = 'PAT', 'Patrimonio'
        INGRESO = 'ING', 'Ingreso'
        GASTO = 'GAS', 'Gasto'
        COSTO = 'COS', 'Costo'

    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=255)
    tipo_cuenta = models.CharField(max_length=3, choices=TipoCuenta.choices)
    es_imputable = models.BooleanField(
        default=True,
        help_text="Indica si esta cuenta puede recibir asientos (True) o si es una cuenta de grupo (False)."
    )

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


# --- ASIENTO CONTABLE ---
class AsientoContable(models.Model):
    TIPO_ASIENTO = [
    ('DIARIO', 'Asiento Diario'),
    ('CIERRE', 'Asiento de Cierre'),
]

    periodo = models.ForeignKey(PeriodoContable, on_delete=models.PROTECT, related_name="asientos")
    fecha = models.DateField()
    concepto = models.TextField()
    tipo = models.CharField(max_length=10, choices=TIPO_ASIENTO, default='DIARIO')  # 👈 nuevo
    proyecto_relacionado = models.ForeignKey(
        'costos.Proyecto',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="asientos_contables"
    )

    class Meta:
        ordering = ['fecha', 'id']

    def __str__(self):
        return f"Asiento {self.pk} - {self.fecha} - {self.concepto[:40]}"

    def clean(self):
        super().clean()
        if self.periodo and self.periodo.cerrado and self.pk is None:
            raise ValidationError(f"El período '{self.periodo.nombre}' está cerrado.")
        if self.periodo and self.fecha:
            if not (self.periodo.inicio <= self.fecha <= self.periodo.fin):
                raise ValidationError(
                    f"La fecha {self.fecha} está fuera del rango del período '{self.periodo.nombre}'."
                )


# --- DETALLE DEL ASIENTO ---
class DetalleAsiento(models.Model):
    asiento = models.ForeignKey(AsientoContable, on_delete=models.CASCADE, related_name="detalles")
    cuenta = models.ForeignKey(Cuenta, on_delete=models.PROTECT, related_name="movimientos")
    debe = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    haber = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.asiento.pk} | {self.cuenta.nombre} | D: {self.debe} | H: {self.haber}"

    def clean(self):
        if self.debe < 0 or self.haber < 0:
            raise ValidationError("Los montos no pueden ser negativos.")
        if self.debe > 0 and self.haber > 0:
            raise ValidationError("Una línea no puede tener Debe y Haber al mismo tiempo.")


# --- SALDO DE CUENTA ---
class SaldoCuenta(models.Model):
    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE)
    periodo = models.ForeignKey(PeriodoContable, on_delete=models.CASCADE)

    # Saldos iniciales
    saldo_inicial_debe = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    saldo_inicial_haber = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    # Movimientos del mes
    total_debe_mes = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_haber_mes = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    # Saldos finales
    saldo_final_deudor = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    saldo_final_acreedor = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        unique_together = ('cuenta', 'periodo')

    def __str__(self):
        return f"Saldo {self.cuenta.nombre} - {self.periodo.nombre}"



# --- ESTIMACIÓN DE COSTOS INDIRECTOS ---
class EstimacionCostoIndirectoGlobal(models.Model):
    nombre = models.CharField(max_length=200, unique=True,
                              help_text="Ej: Alquiler, Luz, Sueldos administrativos, etc.")
    monto_estimado_mensual = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Estimación de Costo Indirecto Global"
        verbose_name_plural = "Estimaciones de Costos Indirectos Globales"

    def __str__(self):
        return f"{self.nombre} (Estimado: ${self.monto_estimado_mensual})"


# --- PARÁMETROS GLOBALES ---
class ParametrosGlobales(models.Model):
    patronal_seguro_social = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0750'))
    patronal_afp = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0875'))
    empleado_seguro_social = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0300'))
    empleado_afp = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0725'))
    dias_laborados_semana = models.IntegerField(default=5)
    horas_laboradas_diarias = models.IntegerField(default=8)
    recargo_vacaciones = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.30'))
    eficiencia_base = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.85'))

    horas_directas_estimadas_mensual = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('1000.00'),
        help_text="Horas directas estimadas por mes"
    )
    tasa_gastos_indirectos_por_hora = models.DecimalField(
        max_digits=10, decimal_places=4, default=Decimal('0.00'),
        editable=False
    )
    porcentaje_iva = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.13'), # Valor actual de El Salvador (13%)
        help_text="Tasa de IVA como decimal (ej: 0.13 para 13%)"
    )

    def save(self, *args, **kwargs):
        if not self.pk and ParametrosGlobales.objects.exists():
            raise ValidationError('Solo puede existir una instancia de ParametrosGlobales.')
        super().save(*args, **kwargs)

    def __str__(self):
        return "Parámetros Globales de la Empresa"

    def calcular_y_guardar_tasa_indirectos(self, recalcular=False, commit=True):
        """
        Suma todas las estimaciones de costos indirectos,
        divide por las horas directas estimadas y actualiza la tasa.
        """
        if self.tasa_gastos_indirectos_por_hora == Decimal('0.00') or recalcular:
            suma_estimaciones = EstimacionCostoIndirectoGlobal.objects.aggregate(
                total=Sum('monto_estimado_mensual')
            )['total'] or Decimal('0.00')

            if self.horas_directas_estimadas_mensual > 0:
                tasa = suma_estimaciones / self.horas_directas_estimadas_mensual
            else:
                tasa = Decimal('0.00')

            self.tasa_gastos_indirectos_por_hora = round(tasa, 4)
            if commit:
                self.save(update_fields=['tasa_gastos_indirectos_por_hora'])
