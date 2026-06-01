from django.urls import include, path

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views


router = DefaultRouter()
router.register(r'articles', views.ArticleViewSet, basename='article')
router.register(r'publishers', views.PublisherViewSet, basename='publisher')
router.register(r'newsletters', views.NewsletterViewSet, basename='newsletter')
router.register(r'users', views.UserViewSet, basename='user')


urlpatterns = [
    path('', views.home, name='home'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    path(
        'reader/dashboard/',
        views.reader_dashboard,
        name='reader_dashboard',
    ),
    path(
        'journalist/dashboard/',
        views.journalist_dashboard,
        name='journalist_dashboard',
    ),
    path(
        'editor/dashboard/',
        views.editor_dashboard,
        name='editor_dashboard',
    ),

    # Article browser pages
    path('articles/', views.article_list, name='article_list'),
    path('articles/create/', views.article_create, name='article_create'),
    path(
        'articles/<int:article_id>/',
        views.article_detail,
        name='article_detail',
    ),
    path(
        'articles/<int:article_id>/edit/',
        views.article_update,
        name='article_update',
    ),
    path(
        'articles/<int:article_id>/delete/',
        views.article_delete,
        name='article_delete',
    ),

    # Newsletter browser pages
    path('newsletters/', views.newsletter_list, name='newsletter_list'),
    path(
        'newsletters/create/',
        views.newsletter_create,
        name='newsletter_create',
    ),
    path(
        'newsletters/<int:newsletter_id>/edit/',
        views.newsletter_update,
        name='newsletter_update',
    ),
    path(
        'newsletters/<int:newsletter_id>/delete/',
        views.newsletter_delete,
        name='newsletter_delete',
    ),

    # Publisher browser pages
    path('publishers/', views.publisher_list, name='publisher_list'),
    path(
        'publishers/create/',
        views.publisher_create,
        name='publisher_create',
    ),
    path(
        'publishers/<int:publisher_id>/edit/',
        views.publisher_update,
        name='publisher_update',
    ),
    path(
        'publishers/<int:publisher_id>/delete/',
        views.publisher_delete,
        name='publisher_delete',
    ),

    # Reader subscription pages
    path('journalists/', views.journalist_list, name='journalist_list'),
    path(
        'journalists/<int:journalist_id>/subscribe/',
        views.subscribe_journalist,
        name='subscribe_journalist',
    ),
    path(
        'publishers/<int:publisher_id>/subscribe/',
        views.subscribe_publisher,
        name='subscribe_publisher',
    ),
    path(
        'reader/newsletters/',
        views.reader_newsletters,
        name='reader_newsletters',
    ),

    # Editor review pages
    path('editor/review/', views.editor_review, name='editor_review'),
    path(
        'editor/articles/<int:article_id>/approve/',
        views.approve_article,
        name='approve_article',
    ),

    # API routes
    path('api/', include(router.urls)),
    path(
        'api/approved/',
        views.approved_article_log_api,
        name='approved_article_log_api',
    ),
    path(
        'api/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair',
    ),
    path(
        'api/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh',
    ),
]