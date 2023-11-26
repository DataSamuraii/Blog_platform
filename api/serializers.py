from django.contrib.auth import get_user_model
from rest_framework import serializers

from posts.models import Post, Category, Comment, CommentReaction
from users.models import EmailSubscriber, UnbanRequest


class PostSerializer(serializers.ModelSerializer):
    author = serializers.HyperlinkedRelatedField(view_name='api_users_details', read_only=True)
    id = serializers.HyperlinkedRelatedField(view_name='api_post_details', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'category', 'date_scheduled', 'date_published', 'views', 'author',
                  'is_published']
        read_only_fields = ['date_published', 'views']

    def validate(self, attrs):
        """
        Check that only either date_scheduled or is_published is set.
        """
        date_scheduled = attrs.get('date_scheduled')
        is_published = attrs.get('is_published')

        if date_scheduled and is_published:
            raise serializers.ValidationError(
                "A post cannot have both date_scheduled and is_published set. Please choose one."
            )
        return attrs


class CategorySerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedRelatedField(view_name='api_categories_details', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'title', 'description']


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedRelatedField(view_name='api_comments_details', read_only=True)
    author = serializers.HyperlinkedRelatedField(view_name='api_users_details', read_only=True)
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()

    def get_likes_count(self, obj):
        return obj.likes_count

    def get_dislikes_count(self, obj):
        return obj.dislikes_count

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'post', 'timestamp', 'parent_comment',
                  'likes_count', 'dislikes_count', 'is_deleted', 'is_profane', 'is_negative']
        read_only_fields = ['timestamp', 'is_profane', 'is_negative']


class CommentReactionSerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedRelatedField(view_name='api_comment_reactions_details', read_only=True)
    user = serializers.HyperlinkedRelatedField(view_name='api_users_details', read_only=True)

    class Meta:
        model = CommentReaction
        fields = ['id', 'user', 'comment', 'reaction_type']


class CustomUserSerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedRelatedField(view_name='api_users_details', read_only=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'bio', 'social_media', 'is_banned']
        read_only_fields = ['is_banned', 'date_joined']


class EmailSubscriberSerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedRelatedField(view_name='api_email_subscribers_details', read_only=True)
    user = serializers.HyperlinkedRelatedField(view_name='api_users_details', read_only=True)

    class Meta:
        model = EmailSubscriber
        fields = ['id', 'user']


class UnbanRequestSerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedRelatedField(view_name='api_unban_requests_details', read_only=True)
    user = serializers.HyperlinkedRelatedField(view_name='api_users_details', read_only=True)

    class Meta:
        model = UnbanRequest
        fields = ['id', 'user', 'content', 'created_at', 'status']
        read_only_fields = ['created_at', 'status']
