from rest_framework import serializers

from .models import Article, CustomUser, Newsletter, Publisher


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for custom users.
    """

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'role',
            'subscribed_publishers',
            'subscribed_journalists',
        ]


class PublisherSerializer(serializers.ModelSerializer):
    """
    Serializer for publishers.
    """

    class Meta:
        model = Publisher
        fields = [
            'id',
            'name',
            'description',
            'editors',
            'journalists',
        ]


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for articles.
    """

    author_username = serializers.CharField(
        source='author.username',
        read_only=True
    )

    publisher_name = serializers.CharField(
        source='publisher.name',
        read_only=True
    )

    class Meta:
        model = Article
        fields = [
            'id',
            'title',
            'content',
            'author',
            'author_username',
            'publisher',
            'publisher_name',
            'created_at',
            'approved',
        ]

        read_only_fields = [
            'author',
            'created_at',
            'approved',
            'author_username',
            'publisher_name',
        ]


class NewsletterSerializer(serializers.ModelSerializer):
    """
    Serializer for newsletters.
    """

    author_username = serializers.CharField(
        source='author.username',
        read_only=True
    )

    class Meta:
        model = Newsletter
        fields = [
            'id',
            'title',
            'description',
            'created_at',
            'author',
            'author_username',
            'articles',
        ]

        read_only_fields = [
            'created_at',
            'author_username',
        ]