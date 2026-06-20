from django.db import models


class Camera(models.Model):
    TIPO_STRUTTURA = [
        ('BEB', 'B&B'),
        ('CASA', 'Casa Vacanze'),
    ]

    nome = models.CharField(max_length=100)
    descrizione = models.TextField()
    prezzo = models.DecimalField(max_digits=6, decimal_places=2)
    immagine = models.ImageField(upload_to="camere/")
    capienza = models.PositiveIntegerField(default=2) 
    tipo_struttura = models.CharField(
        max_length=5,
        choices=TIPO_STRUTTURA,
        default='BEB',
        verbose_name="Tipo di struttura"
    )

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_struttura_display()})"

class Prenotazione(models.Model):
    nome_cliente = models.CharField(max_length=100)
    email = models.EmailField()
    data_checkin = models.DateField()
    data_checkout = models.DateField()
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nome_cliente} - {self.camera.nome}"
