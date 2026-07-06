from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Warehouse, Product
from .serializers import WarehouseSerializer, ProductSerializer, ProductMoveSerializer


class WarehouseViewSet(viewsets.ModelViewSet):
    """
    CRUD complet sur /api/warehouses/ (list, retrieve, create, update, delete)
    + action métier /api/warehouses/{id}/audit/
    """
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=["get"])
    def audit(self, request, pk=None): #audit est une action personnalisée qui permet de récupérer des statistiques sur un entrepôt spécifique.
        """
        GET /api/warehouses/{id}/audit/
        Retourne le nombre total de produits + quelques stats utiles.
        """
        warehouse = self.get_object()
        products = warehouse.products.all()

        
        #by_status est un dictionnaire qui contient le nombre de produits par statut (disponible, réservé, périmé) pour l'entrepôt spécifié.
        by_status = { 
            value: products.filter(status=value).count()
            for value, _ in Product.Status.choices
        }


        #data est un dictionnaire qui contient les informations de l'entrepôt, le nombre total de produits, la quantité totale de produits et le nombre de produits par statut.
        data = {
            "warehouse": warehouse.name,
            "capacity": warehouse.capacity,
            "total_products": products.count(),
            "total_quantity": sum(p.quantity for p in products),
            "by_status": by_status,
        }
        return Response(data, status=status.HTTP_200_OK)


class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD complet sur /api/products/
    + action métier /api/products/{id}/move/
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=["post"])
    def move(self, request, pk=None):
        """
        POST /api/products/{id}/move/
        Body attendu : {"warehouse_id": 3}
        Règle métier : un produit périmé ne peut pas être transféré.
        """
        product = self.get_object()

        if product.is_expired or product.status == Product.Status.EXPIRED:
            return Response(
                {"error": "Impossible de transférer un produit périmé."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ProductMoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_warehouse = Warehouse.objects.get(
            pk=serializer.validated_data["warehouse_id"]
        )
        product.warehouse = new_warehouse
        product.save()

        return Response(
            ProductSerializer(product).data,
            status=status.HTTP_200_OK,
        )
