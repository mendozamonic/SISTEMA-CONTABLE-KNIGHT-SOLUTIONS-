from django.db import models

class EstimacionUCP(models.Model):
    nombre = models.CharField(max_length=150)
    horas_totales = models.DecimalField(max_digits=10, decimal_places=2)
    usado = models.BooleanField(default=False)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} - {self.horas_totales}h"
