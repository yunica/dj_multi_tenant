from django.db import models


# Create your models here.


class Publicacion(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    dcreate = models.DateTimeField(auto_now_add=True)
    dupdate = models.DateTimeField(auto_now=True)
