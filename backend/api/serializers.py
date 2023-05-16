import base64

from django.core.files.base import ContentFile
from recipe.models import (Component, Favorite, Ingredient, Recipe,
                           ShoppingCart, Tag)
from rest_framework import serializers
from users.models import Subscribe, User

from .utils import ingredients_set


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class ComponentSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = Component
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class AuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed',)
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return Subscribe.objects.filter(
            user=user.id,
            author=obj).exists()


class RecipeListSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    ingredients = ComponentSerializer(many=True, source='components')
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time',)
        read_only_fields = (
            'is_favorite',
            'is_shopping_cart',
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=user.id,
            recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=user.id,
            recipe=obj).exists()


class ComponentCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = Component
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = ComponentCreateSerializer(many=True)
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time',)
        read_only_fields = (
            'is_favorite',
            'is_shopping_cart',
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return Favorite.objects.filter(
            user=user.id,
            recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return ShoppingCart.objects.filter(
            user=user.id,
            recipe=obj).exists()

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        cooking_time = self.initial_data.get('cooking_time')

        if not ingredients:
            raise serializers.ValidationError('Вы не указали ингредиенты')
        if not tags:
            raise serializers.ValidationError('Вы не указали категории')

        cached_ingredient_id = set()
        for ingredient in ingredients:
            if int(ingredient['id']) in cached_ingredient_id:
                raise serializers.ValidationError(
                    'Ингредиенты не могут повторяться'
                )
            cached_ingredient_id.add(ingredient['id'])

            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(
                    'Некорректный ввод количества ингредиентов'
                )

        if int(cooking_time) <= 0:
            raise serializers.ValidationError(
                'Некорректный ввод времени готовки'
            )
        return data

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data

    def create(self, validated_data):
        """
        При POST-запросе создаем объект Рецепт,
        добавляем в него теги и компоненты.
        """
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context.get('request').user
        )
        recipe.tags.set(tags)
        ingredients_set(
            recipe=recipe,
            ingredients_data=ingredients_data
        )

        return recipe

    def update(self, instance, validated_data):
        """При PATCH-запросе переопределяем поля рецепта на новые."""
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)

        if validated_data['ingredients']:
            # Удаляем старые компоненты
            instance.ingredients.clear()
            # Устанавливаем новые
            ingredients_set(
                recipe=Recipe.objects.get(pk=instance.id),
                ingredients_data=validated_data['ingredients']
            )

        if validated_data['tags']:
            instance.tags.clear()
            instance.tags.set(validated_data['tags'])

        instance.save()
        return instance


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='recipe',
        read_only=True)
    name = serializers.ReadOnlyField(
        source='recipe.name',
        read_only=True)
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='recipe',
        read_only=True)
    name = serializers.ReadOnlyField(
        source='recipe.name',
        read_only=True)
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True)
    coocking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'coocking_time')


class RecipeForSubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода рецептов при подписке."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image',)
