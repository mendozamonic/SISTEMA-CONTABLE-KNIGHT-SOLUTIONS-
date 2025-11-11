from django.db import models

class Proyecto(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Proyecto")
    cliente = models.CharField(max_length=200, verbose_name="Cliente")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Precio de Venta")
    costo_total_estimado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Costo Total Estimado")
    
    class Meta:
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.nombre} - {self.cliente}"
