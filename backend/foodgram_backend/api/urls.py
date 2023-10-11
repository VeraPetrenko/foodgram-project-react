from django.contrib import admin
from django.urls import path, include


from rest_framework.routers import DefaultRouter

from api.views import (
    CustomUserViewSet,
    RecipeViewSet,
    IngredientViewSet,
    TagViewSet,
    FollowViewSet,
)

router = DefaultRouter()
router_sub = DefaultRouter()
router_sub.register(
    r'users/(?P<following_id>\d+)/subscribe',
    FollowViewSet,
    basename='subscribe'
)
router_sub.register(
    r'users/subscriptions',
    FollowViewSet,
    basename='subscriptions'
)
router.register(
    'users',
    CustomUserViewSet
)
router.register(
    'tags',
    TagViewSet
)
router.register(
    'recipes',
    RecipeViewSet
)
router.register(
    'ingredients',
    IngredientViewSet
)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_sub.urls)),
    path('', include(router.urls))
]
