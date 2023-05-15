from api.pagination import CustomPagination
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipe.models import (Component, Favorite, Ingredient, Recipe,
                           ShoppingCart, Tag)
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeListSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)
from .utils import create_content


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeSerializer

    def _handle_post_request(self, request=None, serializer=None, user=None,
                             model=None, error_message=None, recipe=None):
        """
        Обрабатывает POST-запрос и возвращает ответ в формате JSON.
        """
        serializer = serializer(data={
            'user': user.id,
            'recipe': recipe.id,
        }, context={"request": request})

        try:
            serializer.is_valid(raise_exception=True)
        except serializer.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save(user=user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _handle_delete_request(self, recipe=None, user=None,
                               model=None, error_message=None):
        """
        Обрабатывает DELETE-запрос и возвращает ответ в формате JSON.
        """
        if not model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )

        model.objects.get(user=user, recipe=recipe).delete()

        return Response(
            {'message': 'Рецепт успешно удален.'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        user = request.user
        model = ShoppingCart

        if request.method == 'POST':
            return self._handle_post_request(
                request=request,
                serializer=ShoppingCartSerializer,
                user=user,
                model=model,
                error_message='Рецепт уже есть в списке покупок',
                recipe=recipe,
            )

        return self._handle_delete_request(
            recipe=recipe,
            user=user,
            model=model,
            error_message='Рецепта не было в списке покупок'
        )

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        user = request.user
        model = Favorite

        if request.method == 'POST':
            return self._handle_post_request(
                request=request,
                serializer=FavoriteSerializer,
                user=user,
                model=model,
                error_message='Рецепт уже есть в избранном',
                recipe=recipe,
            )

        return self._handle_delete_request(
            recipe=recipe,
            user=user,
            model=model,
            error_message='Рецепта не было в избранном'
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

        content = create_content(ingredients=ingredients)
        file_name = 'shopping_list.txt'
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return response


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
