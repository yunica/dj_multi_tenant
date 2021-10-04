from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from uuid import uuid1


class AuditModel(models.Model):
    id = models.UUIDField(default=uuid1, primary_key=True, unique=True)
    fregister = models.DateTimeField(auto_now_add=True)
    fupdate = models.DateTimeField(auto_now=True)
    flag = models.BooleanField(default=True)
    flag_adm = models.BooleanField(default=True)

    class Meta:
        abstract = True


class AuditModelIdNumeric(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    fregister = models.DateTimeField(auto_now_add=True)
    fupdate = models.DateTimeField(auto_now=True)
    flag = models.BooleanField(default=True)
    flag_adm = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Mercado(AuditModelIdNumeric):
    nombre_mercado = models.CharField(max_length=100)
    sucursal = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nombre_mercado}"


class Cargo(models.Model):
    nombre = models.CharField(max_length=70, unique=True)
    abre = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nombre


class CustomUserManager(UserManager):  # username mayus minusc
    def get_by_natural_key(self, username):
        case_insensitive_username_field = "{}__iexact".format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})

    def get_nombre_completo(self):
        return "{} {} {}".format(
            self.first_name, self.ap_paterno.upper(), self.ap_materno.upper()
        )

    def get_nombre_incompleto(self):
        return "{} {} ".format(self.first_name, self.ap_paterno.lower())

    # bloqueo
    def agregar_contador_logi(self):
        self.intento += 1
        self.save()
        return self.intento

    def reiniciar_contador_logi(self):
        self.intento = 0
        self.ultimo_intento = None
        self.save()

    def get_is_bloqueado(self, hoy=timezone.localtime()):
        """
        :param hoy: timezone
        :return: true: bloqueado
        """
        if not self.is_bloqueado and self.intento <= 9:
            return False
        if self.intento <= 9:
            if self.intento <= 5:
                return False
            else:
                intervalo = hoy - self.ultimo_intento
                if intervalo.days >= 1 or intervalo.seconds / 60 >= 5:
                    return False
            return True
        else:
            self.is_bloqueado = True
            self.save()
        return True

    @transaction.atomic()
    def get_msj_bloquedo(self):
        ahora = timezone.localtime()
        if self.intento == 5:
            self.ultimo_intento = ahora + timedelta(minutes=5)
            self.save()
            return "Quinto intento, vuelve a intentar en  5 minutos"
        elif self.intento > 5:
            if self.ultimo_intento > ahora:
                resta = self.ultimo_intento - ahora
                return "Intente nuevamente en {}:{} , intento  {}".format(
                    resta.seconds // 60, resta.seconds % 60, self.intento
                )
            return "Ocurrio un error, intento {} de 10 ".format(self.intento)
        return "Ocurrio un error, intento {} de 5".format(self.intento)


SEXO = (
    ("VARON", "VARON"),
    ("MUJER", "MUJER"),
)


class User(AbstractUser, AuditModel):
    ap_paterno = models.CharField(max_length=100, blank=True, default="")
    ap_materno = models.CharField(max_length=100, blank=True, default="")
    sexo = models.CharField(choices=SEXO, max_length=10, blank=True, default="")
    num_documento = models.CharField(max_length=12, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to="fotoperfil/", blank=True, null=True)
    cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT, blank=True, null=True)
    descripcion = models.TextField(blank=True, default="")
    mercado = models.ForeignKey(
        Mercado, on_delete=models.PROTECT, blank=True, null=True
    )
    sucursal = models.CharField(max_length=100, blank=True, default="")
    # intento
    intento = models.SmallIntegerField(default=0)
    ultimo_intento = models.DateTimeField(blank=True, null=True)
    is_bloqueado = models.BooleanField(default=False)
    #
    objects = CustomUserManager()

    def __str__(self):
        return "({}) {} {} {}".format(
            self.cargo,
            self.first_name,
            self.ap_paterno.upper(),
            self.ap_materno.upper(),
        )

