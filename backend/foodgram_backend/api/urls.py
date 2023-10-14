from django.contrib import admin
from django.urls import path, include


from rest_framework.routers import DefaultRouter

from api.views import (
    CustomUserViewSet,
    RecipeViewSet,
    IngredientViewSet,
    TagViewSet,
    FollowViewSet,
    FollowListViewSet,
    FavoriteViewSet,
)

router = DefaultRouter()
router_sub_fav = DefaultRouter()
router_sub_fav.register(
    r'users/(?P<following_id>\d+)/subscribe',
    FollowViewSet,
    basename='subscribe'
)
router_sub_fav.register(
    r'users/subscriptions',
    FollowListViewSet,
    basename='subscriptions'
)
router_sub_fav.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteViewSet,
    basename='subscribe'
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
    path('', include(router_sub_fav.urls)),
    path('', include(router.urls))
]
