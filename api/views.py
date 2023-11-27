from django.contrib.auth import get_user_model, authenticate, login
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from posts.models import Post, Category, Comment, CommentReaction
from users.models import EmailSubscriber, UnbanRequest
from . import permissions as custom_permissions
from . import serializers


# TODO filtering, sorting, and searching
# TODO pagination


class LoginView(generics.GenericAPIView):
    serializer_class = serializers.LoginSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({'message': 'User logged in successfully'}, status=status.HTTP_200_OK)
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer
    permission_classes = [custom_permissions.HasAddPostPermission]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetails(generics.RetrieveUpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer
    permission_classes = [custom_permissions.PostPermission]


class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CategoryDetails(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = serializers.PostSerializer


class CommentList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentDetails(generics.RetrieveUpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = [custom_permissions.CommentPermission]


class CommentReactionList(generics.ListCreateAPIView):
    queryset = CommentReaction.objects.all()
    serializer_class = serializers.CommentReactionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentReactionDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = CommentReaction.objects.all()
    serializer_class = serializers.CommentReactionSerializer
    permission_classes = [custom_permissions.CommentReactionPermission]


class UserList(generics.ListCreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = serializers.CustomUserSerializer
    permission_classes = [custom_permissions.HasViewUserPermission]


class UserDetails(generics.RetrieveUpdateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = serializers.CustomUserSerializer
    permission_classes = [custom_permissions.CustomUserPermission]


class EmailSubscriberList(generics.ListCreateAPIView):
    queryset = EmailSubscriber.objects.all()
    serializer_class = serializers.EmailSubscriberSerializer
    permission_classes = [custom_permissions.HasViewEmailSubscriberPermission]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EmailSubscriberDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = EmailSubscriber.objects.all()
    serializer_class = serializers.EmailSubscriberSerializer
    permission_classes = [custom_permissions.EmailSubscriberPermission]


class UnbanRequestList(generics.ListCreateAPIView):
    queryset = UnbanRequest.objects.all()
    serializer_class = serializers.UnbanRequestSerializer
    permission_classes = [custom_permissions.HasViewUnbanRequestPermission]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UnbanRequestDetails(generics.RetrieveUpdateAPIView):
    queryset = UnbanRequest.objects.all()
    serializer_class = serializers.UnbanRequestSerializer
    permission_classes = [custom_permissions.UnbanRequestPermission]
