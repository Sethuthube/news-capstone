import requests

from functools import wraps

from django.conf import settings
from django.contrib import messages
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

from .forms import (
    ArticleForm,
    NewsletterForm,
    PublisherForm,
    RegisterForm,
)
from .models import (
    ApprovedArticleLog,
    Article,
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
    """Display the public home page."""
    return render(request, 'news/home.html')


def register_view(request):
    """Register a new user and log them in."""
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
    """Authenticate users and redirect them based on their role."""
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
    """Log out the current user."""
    logout(request)
    return redirect('home')


@login_required
def dashboard_view(request):
    """Send each user to the correct dashboard for their role."""
    if request.user.role == 'reader':
        return redirect('reader_dashboard')

    if request.user.role == 'journalist':
        return redirect('journalist_dashboard')

    if request.user.role == 'editor':
        return redirect('editor_dashboard')

    return redirect('home')


def role_required(required_role):
    """
    Restrict a view to users with a specific role.

    Superusers are allowed through so the project can still be tested easily
    from the admin account.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user_has_role = (
                request.user.is_authenticated
                and request.user.role == required_role
            )

            if user_has_role or request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden(
                'You do not have permission to access this page.'
            )

        return wrapper

    return decorator


@login_required
@role_required('reader')
def reader_dashboard(request):
    """Display the reader dashboard."""
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
    """Display the journalist dashboard and their own content."""
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
    """Display articles available for editor review."""
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
    Notify subscribed readers when an article is approved.

    The task allows the approval logic to happen directly in the approval view
    instead of Django signals. This function supports that approach.

    It checks:
    1. Readers subscribed to the article publisher.
    2. Readers subscribed to the article journalist/author.

    It also logs the approved article in the ApprovedArticleLog model.
    """
    subscriber_emails = set()

    if article.publisher:
        publisher_subscribers = CustomUser.objects.filter(
            role='reader',
            subscribed_publishers=article.publisher
        )

        for user in publisher_subscribers:
            if user.email:
                subscriber_emails.add(user.email)

    if article.author:
        journalist_subscribers = CustomUser.objects.filter(
            role='reader',
            subscribed_journalists=article.author
        )

        for user in journalist_subscribers:
            if user.email:
                subscriber_emails.add(user.email)

    if subscriber_emails:
        send_mail(
            subject=f'New approved article: {article.title}',
            message=(
                f'A new article has been approved and published.\n\n'
                f'Title: {article.title}\n\n'
                f'{article.content}'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=list(subscriber_emails),
            fail_silently=False,
        )

    ApprovedArticleLog.objects.get_or_create(article=article)

    if request:
        messages.success(
            request,
            f'Article "{article.title}" was approved and subscribers were notified.'
        )


def article_list(request):
    """Show all approved articles to readers."""
    articles = Article.objects.filter(approved=True).order_by('-created_at')

    return render(
        request,
        'news/article_list.html',
        {'articles': articles}
    )


def article_detail(request, article_id):
    """Show one approved article."""
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
    """Allow editors to review unapproved articles."""
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
    """Allow editors to approve articles from the web interface."""
    if request.user.role != 'editor' and not request.user.is_superuser:
        return redirect('article_list')

    article = get_object_or_404(Article, id=article_id)
    article.approved = True
    article.save()

    notify_article_approval(article, request)

    return redirect(reverse('editor_review'))


class ArticleViewSet(viewsets.ModelViewSet):
    """API endpoint for articles."""
    serializer_class = ArticleSerializer
    permission_classes = [ArticlePermission]

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Article.objects.filter(approved=True).order_by(
                '-created_at'
            )

        if user.is_superuser or user.role == 'editor':
            return Article.objects.all().order_by('-created_at')

        if user.role == 'journalist':
            return Article.objects.filter(author=user).order_by('-created_at')

        return Article.objects.filter(approved=True).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, approved=False)

    @action(detail=False, methods=['get'], url_path='subscribed')
    def subscribed(self, request):
        """Return approved articles from the reader's subscriptions."""
        user = request.user

        if user.role != 'reader' and not user.is_superuser:
            return Response(
                {'error': 'Only readers can view subscribed articles.'},
                status=status.HTTP_403_FORBIDDEN
            )

        publisher_ids = user.subscribed_publishers.values_list(
            'id',
            flat=True
        )
        journalist_ids = user.subscribed_journalists.values_list(
            'id',
            flat=True
        )

        publisher_articles = Article.objects.filter(
            approved=True,
            publisher_id__in=publisher_ids
        )

        journalist_articles = Article.objects.filter(
            approved=True,
            author_id__in=journalist_ids
        )

        articles = (
            publisher_articles | journalist_articles
        ).distinct().order_by('-created_at')

        serializer = self.get_serializer(articles, many=True)

        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsEditor],
        url_path='approve'
    )
    def approve(self, request, pk=None):
        """Allow editors to approve articles from the API."""
        article = self.get_object()
        article.approved = True
        article.save()

        notify_article_approval(article, request)

        serializer = self.get_serializer(article)

        return Response(serializer.data)


class PublisherViewSet(viewsets.ModelViewSet):
    """API endpoint for publishers."""
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [IsAuthenticated]


class NewsletterViewSet(viewsets.ModelViewSet):
    """API endpoint for newsletters."""
    queryset = Newsletter.objects.all().order_by('-created_at')
    serializer_class = NewsletterSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only API endpoint for users."""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approved_article_log_api(request):
    """Internal API endpoint to log approved articles."""
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

    ApprovedArticleLog.objects.get_or_create(article=article)

    return Response(
        {'message': 'Approved article logged successfully.'},
        status=status.HTTP_201_CREATED
    )


@login_required
def article_create(request):
    """Allow journalists and editors to create a new article."""
    allowed_roles = ['journalist', 'editor']

    if request.user.role not in allowed_roles and not request.user.is_superuser:
        return HttpResponseForbidden(
            'You are not allowed to create articles.'
        )

    if request.method == 'POST':
        form = ArticleForm(request.POST)

        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.approved = False
            article.save()
            form.save_m2m()

            messages.success(request, 'Article submitted for review.')
            return redirect('article_list')
    else:
        form = ArticleForm()

    return render(
        request,
        'news/article_form.html',
        {'form': form, 'title': 'Create Article'}
    )


@login_required
def article_update(request, article_id):
    """Allow article authors, editors, or admins to update an article."""
    article = get_object_or_404(Article, id=article_id)

    allowed_user = article.author == request.user
    allowed_role = request.user.role == 'editor' or request.user.is_superuser

    if not allowed_user and not allowed_role:
        return HttpResponseForbidden(
            'You are not allowed to edit this article.'
        )

    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)

        if form.is_valid():
            form.save()
            messages.success(request, 'Article updated successfully.')
            return redirect('article_detail', article_id=article.id)
    else:
        form = ArticleForm(instance=article)

    return render(
        request,
        'news/article_form.html',
        {'form': form, 'title': 'Update Article'}
    )


@login_required
def article_delete(request, article_id):
    """Allow article authors, editors, or admins to delete an article."""
    article = get_object_or_404(Article, id=article_id)

    allowed_user = article.author == request.user
    allowed_role = request.user.role == 'editor' or request.user.is_superuser

    if not allowed_user and not allowed_role:
        return HttpResponseForbidden(
            'You are not allowed to delete this article.'
        )

    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Article deleted successfully.')
        return redirect('article_list')

    return render(
        request,
        'news/article_confirm_delete.html',
        {'article': article}
    )


@login_required
def newsletter_list(request):
    """Display a list of newsletters."""
    newsletters = Newsletter.objects.all().order_by('-created_at')

    return render(
        request,
        'news/newsletter_list.html',
        {'newsletters': newsletters}
    )


@login_required
def newsletter_create(request):
    """Allow journalists and editors to create newsletters."""
    allowed_roles = ['journalist', 'editor']

    if request.user.role not in allowed_roles and not request.user.is_superuser:
        return HttpResponseForbidden(
            'You are not allowed to create newsletters.'
        )

    if request.method == 'POST':
        form = NewsletterForm(request.POST)

        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.author = request.user
            newsletter.save()
            form.save_m2m()

            messages.success(request, 'Newsletter created successfully.')
            return redirect('newsletter_list')
    else:
        form = NewsletterForm()

    return render(
        request,
        'news/newsletter_form.html',
        {'form': form, 'title': 'Create Newsletter'}
    )


@login_required
def newsletter_update(request, newsletter_id):
    """Allow newsletter authors, editors, or admins to update newsletters."""
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)

    allowed_user = newsletter.author == request.user
    allowed_role = request.user.role == 'editor' or request.user.is_superuser

    if not allowed_user and not allowed_role:
        return HttpResponseForbidden(
            'You are not allowed to edit this newsletter.'
        )

    if request.method == 'POST':
        form = NewsletterForm(request.POST, instance=newsletter)

        if form.is_valid():
            form.save()
            messages.success(request, 'Newsletter updated successfully.')
            return redirect('newsletter_list')
    else:
        form = NewsletterForm(instance=newsletter)

    return render(
        request,
        'news/newsletter_form.html',
        {'form': form, 'title': 'Update Newsletter'}
    )


@login_required
def newsletter_delete(request, newsletter_id):
    """Allow newsletter authors, editors, or admins to delete newsletters."""
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)

    allowed_user = newsletter.author == request.user
    allowed_role = request.user.role == 'editor' or request.user.is_superuser

    if not allowed_user and not allowed_role:
        return HttpResponseForbidden(
            'You are not allowed to delete this newsletter.'
        )

    if request.method == 'POST':
        newsletter.delete()
        messages.success(request, 'Newsletter deleted successfully.')
        return redirect('newsletter_list')

    return render(
        request,
        'news/newsletter_confirm_delete.html',
        {'newsletter': newsletter}
    )


@login_required
def publisher_list(request):
    """Display a list of publishers."""
    publishers = Publisher.objects.all()

    return render(
        request,
        'news/publisher_list.html',
        {'publishers': publishers}
    )


@login_required
def publisher_create(request):
    """Allow editors and admins to create publishers."""
    if request.user.role != 'editor' and not request.user.is_superuser:
        return HttpResponseForbidden(
            'You are not allowed to create publishers.'
        )

    if request.method == 'POST':
        form = PublisherForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Publisher created successfully.')
            return redirect('publisher_list')
    else:
        form = PublisherForm()

    return render(
        request,
        'news/publisher_form.html',
        {'form': form, 'title': 'Create Publisher'}
    )


@login_required
def publisher_update(request, publisher_id):
    """Allow editors and admins to update publishers."""
    if request.user.role != 'editor' and not request.user.is_superuser:
        return HttpResponseForbidden(
            'You are not allowed to edit publishers.'
        )

    publisher = get_object_or_404(Publisher, id=publisher_id)

    if request.method == 'POST':
        form = PublisherForm(request.POST, instance=publisher)

        if form.is_valid():
            form.save()
            messages.success(request, 'Publisher updated successfully.')
            return redirect('publisher_list')
    else:
        form = PublisherForm(instance=publisher)

    return render(
        request,
        'news/publisher_form.html',
        {'form': form, 'title': 'Update Publisher'}
    )


@login_required
def publisher_delete(request, publisher_id):
    """Allow editors and admins to delete publishers."""
    if request.user.role != 'editor' and not request.user.is_superuser:
        return HttpResponseForbidden(
            'You are not allowed to delete publishers.'
        )

    publisher = get_object_or_404(Publisher, id=publisher_id)

    if request.method == 'POST':
        publisher.delete()
        messages.success(request, 'Publisher deleted successfully.')
        return redirect('publisher_list')

    return render(
        request,
        'news/publisher_confirm_delete.html',
        {'publisher': publisher}
    )


@login_required
def journalist_list(request):
    """Display journalists so readers can subscribe to them."""
    journalists = CustomUser.objects.filter(role='journalist')

    return render(
        request,
        'news/journalist_list.html',
        {'journalists': journalists}
    )


@login_required
def subscribe_journalist(request, journalist_id):
    """Allow readers to subscribe to a journalist."""
    if request.user.role != 'reader' and not request.user.is_superuser:
        messages.error(request, 'Only readers can subscribe to journalists.')
        return redirect('reader_dashboard')

    journalist = get_object_or_404(
        CustomUser,
        id=journalist_id,
        role='journalist'
    )

    request.user.subscribed_journalists.add(journalist)

    messages.success(
        request,
        f'You have successfully subscribed to {journalist.username}.'
    )

    return redirect('reader_dashboard')


@login_required
def subscribe_publisher(request, publisher_id):
    """Allow readers to subscribe to a publisher."""
    if request.user.role != 'reader' and not request.user.is_superuser:
        messages.error(request, 'Only readers can subscribe to publishers.')
        return redirect('reader_dashboard')

    publisher = get_object_or_404(Publisher, id=publisher_id)

    request.user.subscribed_publishers.add(publisher)

    messages.success(
        request,
        f'You have successfully subscribed to {publisher.name}.'
    )

    return redirect('reader_dashboard')


@login_required
def reader_newsletters(request):
    """Display newsletters for readers."""
    newsletters = Newsletter.objects.all().order_by('-created_at')

    return render(
        request,
        'news/reader_newsletters.html',
        {'newsletters': newsletters}
    )