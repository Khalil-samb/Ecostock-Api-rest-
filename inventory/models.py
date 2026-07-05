from django.db import models
from django.utils import timezone


class Warehouse(models.Model):
    """
    Un entrepôt / redistributeur.
    Relation 1-N avec Product : un entrepôt a plusieurs produits,
    un produit appartient à un seul entrepôt.
    """
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField(
        help_text="Capacité maximale de l'entrepôt (nombre d'unités)"
    )

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Un produit alimentaire stocké dans un entrepôt.
    """

    class Status(models.TextChoices):
        AVAILABLE = "disponible", "Disponible"
        RESERVED = "reserve", "Réservé"
        EXPIRED = "perime", "Périmé"

    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=0)
    expiration_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )

    # related_name="products" permet de faire warehouse.products.all()
    warehouse = models.ForeignKey(
        Warehouse,
        related_name="products",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.name} ({self.quantity} unités)"

    @property
    def is_expired(self):
        """Vérifie la péremption en comparant à la date du jour."""
        return self.expiration_date < timezone.now().date()

    def save(self, *args, **kwargs):
        # Auto-synchronisation du statut si la date est dépassée
        if self.is_expired:
            self.status = self.Status.EXPIRED
        super().save(*args, **kwargs)
