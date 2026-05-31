import requests

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .forms import RegisterForm
from .models import (
    Article,
    ApprovedArticleLog,
    CustomUser,
    Newsletter,
    Publisher,
)
from .permissions import ArticlePermission, IsEditor
from .serializers import (
    ArticleSerializer,
    NewsletterSerializer,
    PublisherSerializer,
    UserSerializer,
)

def home(request):
    return render(request, 'news/home.html')


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'news/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'news/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard_view(request):
    if request.user.role == 'reader':
        return redirect('reader_dashboard')

    if request.user.role == 'journalist':
        return redirect('journalist_dashboard')

    if request.user.role == 'editor':
        return redirect('editor_dashboard')
    
    if request.user.role == 'publisher':
        return redirect('publisher_dashboard')

    return redirect('home')


def role_required(required_role):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if (
                request.user.is_authenticated
                and request.user.role == required_role
            ):
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden(
                'You do not have permission to access this page.'
            )

        return wrapper

    return decorator


@login_required
@role_required('reader')
def reader_dashboard(request):
    articles = Article.objects.filter(approved=True).order_by('-created_at')
    newsletters = Newsletter.objects.all().order_by('-created_at')
    publishers = Publisher.objects.all()
    journalists = CustomUser.objects.filter(role='journalist')

    return render(
        request,
        'news/reader_dashboard.html',
        {
            'articles': articles,
            'newsletters': newsletters,
            'publishers': publishers,
            'journalists': journalists,
        }
    )


@login_required
@role_required('journalist')
def journalist_dashboard(request):
    articles = Article.objects.filter(author=request.user).order_by(
        '-created_at'
    )
    newsletters = Newsletter.objects.filter(author=request.user).order_by(
        '-created_at'
    )

    return render(
        request,
        'news/journalist_dashboard.html',
        {
            'articles': articles,
            'newsletters': newsletters,
        }
    )


@login_required
@role_required('editor')
def editor_dashboard(request):
    pending_articles = Article.objects.filter(approved=False).order_by(
        '-created_at'
    )
    approved_articles = Article.objects.filter(approved=True).order_by(
        '-created_at'
    )

    return render(
        request,
        'news/editor_dashboard.html',
        {
            'pending_articles': pending_articles,
            'approved_articles': approved_articles,
        }
    )


def notify_article_approval(article, request=None):
    """
    Notify subscribers and log approved articles to the internal API.
    """

    subscriber_emails = []

    if article.publisher:
        publisher_subscribers = article.publisher.subscribers.all()
        subscriber_emails += [
            user.email for user in publisher_subscribers if user.email
        ]

    journalist_subscribers = article.author.subscribers_to_journalist.all()
    subscriber_emails += [
        user.email for user in journalist_subscribers if user.email
    ]

    if subscriber_emails:
        send_mail(
            subject=f'New approved article: {article.title}',
            message=article.content,
            from_email=None,
            recipient_list=list(set(subscriber_emails)),
            fail_silently=True,
        )

    ApprovedArticleLog.objects.create(article=article)

    if request:
        api_url = request.build_absolute_uri('/api/approved/')

        try:
            requests.post(
                api_url,
                json={'article_id': article.id},
                timeout=5,
            )
        except requests.RequestException:
            pass
        
def article_list(request):
    """
    Show all approved articles to readers.
    """

    articles = Article.objects.filter(approved=True).order_by('-created_at')

    return render(
        request,
        'news/article_list.html',
        {'articles': articles}
    )


def article_detail(request, article_id):
    """
    Show one approved article.
    """

    article = get_object_or_404(
        Article,
        id=article_id,
        approved=True
    )

    return render(
        request,
        'news/article_detail.html',
        {'article': article}
    )


@login_required
def editor_review(request):
    """
    Allow editors to review unapproved articles.
    """

    if request.user.role != 'editor' and not request.user.is_superuser:
        return redirect('article_list')

    articles = Article.objects.filter(approved=False).order_by('-created_at')

    return render(
        request,
        'news/editor_review.html',
        {'articles': articles}
    )


@login_required
@require_POST
def approve_article(request, article_id):
    """
    Allow editors to approve articles.
    """

    if request.user.role != 'editor' and not request.user.is_superuser:
        return redirect('article_list')

    article = get_object_or_404(Article, id=article_id)
    article.approved = True
    article.save()

    notify_article_approval(article, request)

    return redirect(reverse('editor_review'))

class ArticleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for articles.
    """

    serializer_class = ArticleSerializer
    permission_classes = [ArticlePermission]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.role == 'editor':
            return Article.objects.all().order_by('-created_at')

        if user.role == 'journalist':
            return Article.objects.filter(author=user).order_by('-created_at')

        return Article.objects.filter(approved=True).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, approved=False)

    @action(detail=False, methods=['get'], url_path='subscribed')
    def subscribed(self, request):
        """
        Return approved articles from the reader's subscriptions.
        """

        user = request.user

        publisher_ids = user.subscribed_publishers.values_list(
            'id',
            flat=True
        )

        journalist_ids = user.subscribed_journalists.values_list(
            'id',
            flat=True
        )

        articles = Article.objects.filter(
            approved=True,
            publisher_id__in=publisher_ids
        ) | Article.objects.filter(
            approved=True,
            author_id__in=journalist_ids
        )

        serializer = self.get_serializer(
            articles.distinct().order_by('-created_at'),
            many=True
        )

        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsEditor],
        url_path='approve'
    )
    def approve(self, request, pk=None):
        """
        Allow editors to approve articles from the API.
        """

        article = self.get_object()
        article.approved = True
        article.save()

        notify_article_approval(article, request)

        serializer = self.get_serializer(article)

        return Response(serializer.data)


class PublisherViewSet(viewsets.ModelViewSet):
    """
    API endpoint for publishers.
    """

    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [IsAuthenticated]


class NewsletterViewSet(viewsets.ModelViewSet):
    """
    API endpoint for newsletters.
    """

    queryset = Newsletter.objects.all().order_by('-created_at')
    serializer_class = NewsletterSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API endpoint for users.
    """

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approved_article_log_api(request):
    """
    Internal API endpoint to log approved articles.
    """

    article_id = request.data.get('article_id')

    if not article_id:
        return Response(
            {'error': 'article_id is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        article = Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        return Response(
            {'error': 'Article not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    ApprovedArticleLog.objects.create(article=article)

    return Response(
        {'message': 'Approved article logged successfully.'},
        status=status.HTTP_201_CREATED
    )