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

    path('articles/', views.article_list, name='article_list'),
    path(
        'articles/<int:article_id>/',
        views.article_detail,
        name='article_detail',
    ),

    path('editor/review/', views.editor_review, name='editor_review'),
    path(
        'editor/articles/<int:article_id>/approve/',
        views.approve_article,
        name='approve_article',
    ),

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