from rest_framework import serializers
from .models import Warehouse, Product


class ProductSerializer(serializers.ModelSerializer):
    is_expired = serializers.BooleanField(read_only=True) 

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "quantity",
            "expiration_date",
            "status",
            "warehouse",
            "is_expired",
        ]


class WarehouseSerializer(serializers.ModelSerializer):
    # Affiche les produits liés en lecture seule (pratique pour le GET détail)
    products = ProductSerializer(many=True, read_only=True) 

    class Meta:
        model = Warehouse
        fields = ["id", "name", "location", "capacity", "products"]


class ProductMoveSerializer(serializers.Serializer):
    """
    Sérialiseur "à la carte" (pas lié à un modèle) utilisé uniquement
    pour valider le body de la requête POST /products/{id}/move/
    """
    warehouse_id = serializers.IntegerField() #permet de valider que l'ID de l'entrepôt est bien un entier et qu'il correspond à un entrepôt existant dans la base de données.

    def validate_warehouse_id(self, value):
        if not Warehouse.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Cet entrepôt n'existe pas.")
        return value

#la classe ProductMoveSerializer est un sérialiseur personnalisé qui n'est pas directement lié à un modèle Django. 
# Elle est utilisée pour valider les données envoyées dans le corps d'une requête POST lorsqu'on souhaite déplacer un produit vers un autre entrepôt. 
# Le champ warehouse_id est défini comme un entier, et la méthode validate_warehouse_id vérifie si l'entrepôt spécifié existe dans la base de données. 
# Si l'entrepôt n'existe pas, une exception ValidationError est levée avec un message approprié.