from rest_framework import serializers

from .models import Article, CustomUser, Newsletter, Publisher


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for custom users.

    Passwords are intentionally excluded.
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
        read_only_fields = [
            'id',
        ]


class PublisherSerializer(serializers.ModelSerializer):
    """
    Serializer for publishers.

    Editors and journalists are represented by their user IDs.
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

    The author is automatically set in the view when an article is created.
    The API user should not manually choose the article author.
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
            'id',
            'author',
            'author_username',
            'publisher_name',
            'created_at',
            'approved',
        ]


class NewsletterSerializer(serializers.ModelSerializer):
    """
    Serializer for newsletters.

    Articles are selected by ID when creating or updating a newsletter.
    """

    author_username = serializers.CharField(
        source='author.username',
        read_only=True
    )

    article_titles = serializers.SerializerMethodField()

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
            'article_titles',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'author',
            'author_username',
            'article_titles',
        ]

    def get_article_titles(self, obj):
        """
        Return article titles for readable API responses.
        """
        return [article.title for article in obj.articles.all()]