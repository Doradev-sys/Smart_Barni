from django.contrib.auth import get_user_model

from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import UserSerializer
from .permissions import AdminOnly


User = get_user_model()



class RegisterView(generics.CreateAPIView):

    queryset = User.objects.all()

    serializer_class = UserSerializer

    permission_classes = [
        permissions.AllowAny
    ]



class ProfileView(APIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]


    def get(self, request):

        user = request.user

        return Response({

            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "phone": user.phone,

        })



class AdminTestView(APIView):

    permission_classes = [
        AdminOnly
    ]


    def get(self, request):

        return Response({

            "message": "Welcome Admin"

        })