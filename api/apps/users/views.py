import json

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import update_last_login
from django.http import HttpResponse
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, get_object_or_404, CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api.throttling.UserLoginRateThrottle import UserLoginRateThrottle
from api.utils.permissions import IsActiveAdminUser, IsOwner, IsActiveUser, IsAuthenticatedUser
from .models import User
from .serializers import CreateUserSerializer, UserSerializer, UserUpdateSerializer
from ..wallets.models import Wallet


class UserLoginView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (UserLoginRateThrottle,)

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)

        if user and user.is_active:
            refresh = RefreshToken.for_user(user)
            wallet = Wallet.objects.get(user=user)
            response = {
                'user': user.json(),
                'wallet': {
                    'balance': f'{wallet.current_balance}',
                    'last_activity': f'{wallet.modified}'
                },
                'tokens': {
                    'refresh': f'{refresh}',
                    'access': f'{refresh.access_token}',
                },
            }

            update_last_login(None, user)
            return HttpResponse(json.dumps(response), content_type='application/json')

        error = 'Your user account has been deactivated.' if user else 'Invalid Credentials'
        return Response(data={'error': error}, status=HTTP_400_BAD_REQUEST)


class UserCreateView(CreateAPIView):
    model = get_user_model()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)


class UserListView(ListAPIView):
    permission_classes = (IsActiveAdminUser,)
    serializer_class = UserSerializer

    def get_queryset(self):
        filter_kwargs = {}
        only_active = self.request.query_params.get('onlyActive', 'False')

        if only_active.title() == 'True':
            filter_kwargs['is_active'] = True

        return User.objects.exclude(id=self.request.user.id).filter(**filter_kwargs)


class UserDetailsUpdateView(RetrieveUpdateAPIView):
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        return get_object_or_404(User, id=self.kwargs.get(self.lookup_url_kwarg))

    def get_object(self):
        return self.get_queryset()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        if self.request.method == 'PUT':
            return UserUpdateSerializer

    def get_permission_classes(self):
        if self.request.method == 'GET':
            return (IsActiveAdminUser, IsAuthenticatedUser,)
        if self.request.method == 'PUT':
            return (IsActiveAdminUser, IsOwner,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'user_id': self.kwargs.get(self.lookup_url_kwarg)
        })

        return context

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = not instance.is_active
        instance.modified_by = self.request.user
        instance.save()

        return Response(UserSerializer(instance).data, status=HTTP_200_OK)