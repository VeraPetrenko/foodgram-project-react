from django.contrib import admin
from django.urls import path, include


from rest_framework.routers import DefaultRouter

from api.views import (
    CustomUserViewSet,
    RecipeViewSet,
    # IngredientViewSet,
    TagViewSet
)

router = DefaultRouter()
router.register('users', CustomUserViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
