from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User

class SLA(models.Model):
    nombre_sla = models.CharField(max_length=100)
    tiempo_respuesta = models.PositiveIntegerField()
    tiempo_resolucion = models.PositiveIntegerField()
    activo = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.activo:
            # Desactivar los otros SLA activos
            SLA.objects.exclude(id=self.id).update(activo=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre_sla

class TICKET(models.Model):
    PRIORIDADES = (
        ('Alta', 'Alta'),
        ('Media', 'Media'),
        ('Baja', 'Baja'),
        ('Sin asignacion' , 'Sin asignacion')
    )

    ESTADOS = (
    ('Abierto', 'Abierto'),
    ('En proceso', 'En proceso'),
    ('Resuelto', 'Resuelto'),
    ('Cerrado', 'Cerrado'),
    )

    id_usuario_solicitante = models.ForeignKey(User, related_name='tickets_solicitados', on_delete=models.PROTECT, blank=True)
    id_usuario_asignado = models.ForeignKey(User, related_name='tickets_asignados', on_delete=models.PROTECT, blank=True)
    titulo = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=1000)
    prioridad = models.CharField(max_length=15, choices=PRIORIDADES, default='Sin asignacion')
    estado = models.CharField(max_length=35, choices=ESTADOS, default='Abierto')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_primera_respuesta = models.DateTimeField(null=True, blank=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    sla_aplicado = models.ForeignKey(SLA, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.titulo} - {self.prioridad}"
    
    @property
    def resuelto_fuera_de_sla(self):
        if self.estado == 'Resuelto' and self.fecha_resolucion and self.sla_aplicado:
            limite = self.fecha_creacion + timedelta(hours=self.sla_aplicado.tiempo_resolucion)
            return self.fecha_resolucion > limite
        return False

class COMENTARIO(models.Model):
    ticket = models.ForeignKey(TICKET, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comentario = models.TextField()
    fecha_comentario = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario de {self.usuario} en Ticket {self.ticket.id}"

class REPORTE(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tipo_reporte = models.CharField(max_length=255)
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo_reporte} generado por {self.usuario}"
        