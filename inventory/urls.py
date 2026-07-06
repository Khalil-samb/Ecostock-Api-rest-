from rest_framework.routers import DefaultRouter
from .views import WarehouseViewSet, ProductViewSet
from django.urls import path, include

router = DefaultRouter()

router.register("warehouses", WarehouseViewSet, basename="warehouse")
router.register("products", ProductViewSet, basename="product")


urlpatterns = [
  
    path("", include(router.urls))

   
]

# Le router génère automatiquement :
# GET/POST      /warehouses/
# GET/PUT/PATCH/DELETE  /warehouses/{id}/
# GET           /warehouses/{id}/audit/      <-- grace au @action
# GET/POST      /products/
# GET/PUT/PATCH/DELETE  /products/{id}/
# POST          /products/{id}/move/         <-- grace au @action
