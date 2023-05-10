from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

from api.pagination import CustomPagination
from recipe.models import (Component, Favorite, Ingredient, Recipe,
                           ShoppingCart, Tag)
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeListSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        user = request.user

        if request.method == 'POST':
            serializer = ShoppingCartSerializer(data={
                'user': user.id,
                'recipe': kwargs.get('pk'),
            }, context={"request": request})
            if serializer.is_valid():
                # Если рецепт уже есть в списке покупок - рейзим 400
                if ShoppingCart.objects.filter(
                        user=user,
                        recipe=recipe).exists():
                    return Response(
                        {'errors': 'Рецепт уже есть в списке покупок'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                serializer.save(user=user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)

            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            if not ShoppingCart.objects.filter(
                    user=user,
                    recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепта не было в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.get(
                user=user,
                recipe=recipe).delete()
            return Response(
                'Рецепт успешно удален из списка покупок',
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {'errors': 'Данный метод неразрешен'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )

    @action(detail=False,
            methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        # Находим все компоненты пользователя
        components = Component.objects.filter(recipe__shopping_cart__user=user)

        ingredients = components.values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        content = 'Ваш список покупок:\n'

        for ingredient in ingredients:
            content += (f"{ingredient['ingredient__name']} " +
                        f"({ingredient['ingredient__measurement_unit']}) " +
                        f"{ingredient['amount']}" +
                        '\n')

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=shopping_list.txt'
        return response

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        user = request.user

        if request.method == 'POST':
            serializer = FavoriteSerializer(data={
                'user': user.id,
                'recipe': kwargs.get('pk')
            })
            if serializer.is_valid():
                # Если рецепт уже есть в избранном - рейзим 400
                if Favorite.objects.filter(
                        user=user,
                        recipe=recipe).exists():
                    return Response(
                        {'errors': 'Рецепт уже есть в избранном'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                serializer.save(user=user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            if not Favorite.objects.filter(
                    user=user,
                    recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепта не было в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.get(
                user=user,
                recipe=recipe).delete()
            return Response(
                'Рецепт успешно удален из избранного',
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {'errors': 'Данный метод неразрешен'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
