from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response

from api.pagination import CustomPagination

from .models import Subscribe, User
from .serializers import (SubscribeSerializer, UserCreateSerializer,
                          UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return UserSerializer
        return UserCreateSerializer

    @action(detail=False,
            methods=['GET'],
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False,
            methods=['post'],
            permission_classes=(permissions.IsAuthenticated,))
    def set_password(self, request):
        serializer = SetPasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'detail': 'Пароль успешно изменен'},
                            status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])
        user = request.user

        if request.method == 'POST':
            serializer = SubscribeSerializer(data={
                'user': user.id,
                'author': kwargs.get('pk')
            }, context={"request": request})
            if serializer.is_valid(raise_exception=True):
                # Если подписка существет / подписываемся на себя - рейзим 400
                if Subscribe.objects.filter(
                        user=user,
                        author=author).exists() or author == user:
                    return Response(
                        {'errors': 'Ошибка подписки(Вы уже подписаны или пытаетесь подписаться на себя)'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                serializer.save(author=author, user=user)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            if not Subscribe.objects.filter(
                    user=user,
                    author=author).exists():
                return Response(
                    {'errors': 'Ошибка отписки (Вы не были подписаны)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscribe.objects.get(
                user=user,
                author=author).delete()
            return Response(
                'Вы успешно отписаны',
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=False,
            methods=['get'],
            permission_classes=[permissions.IsAuthenticated],
            pagination_class=CustomPagination)
    def subscriptions(self, request):
        user = request.user
        subscribes = Subscribe.objects.filter(
            user=user)
        page = self.paginate_queryset(subscribes)
        serializer = SubscribeSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
