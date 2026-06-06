from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register(r'articles', views.ArticleViewSet, basename='api_articles')
router.register(r'publishers', views.PublisherViewSet, basename='api_publishers')
router.register(
    r'newsletters',
    views.NewsletterViewSet,
    basename='api_newsletters'
)
router.register(r'users', views.UserViewSet, basename='api_users')


urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('articles/', views.article_list, name='article_list'),
    path(
        'articles/<int:article_id>/',
        views.article_detail,
        name='article_detail'
    ),

    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboards
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path(
        'dashboard/reader/',
        views.reader_dashboard,
        name='reader_dashboard'
    ),
    path(
        'dashboard/journalist/',
        views.journalist_dashboard,
        name='journalist_dashboard'
    ),
    path(
        'dashboard/editor/',
        views.editor_dashboard,
        name='editor_dashboard'
    ),

    # Editor approval
    path('editor/review/', views.editor_review, name='editor_review'),
    path(
        'articles/<int:article_id>/approve/',
        views.approve_article,
        name='approve_article'
    ),

    # Article web CRUD
    path('articles/create/', views.article_create, name='article_create'),
    path(
        'articles/<int:article_id>/edit/',
        views.article_update,
        name='article_update'
    ),
    path(
        'articles/<int:article_id>/delete/',
        views.article_delete,
        name='article_delete'
    ),

    # Newsletter web CRUD
    path('newsletters/', views.newsletter_list, name='newsletter_list'),
    path(
        'newsletters/create/',
        views.newsletter_create,
        name='newsletter_create'
    ),
    path(
        'newsletters/<int:newsletter_id>/edit/',
        views.newsletter_update,
        name='newsletter_update'
    ),
    path(
        'newsletters/<int:newsletter_id>/delete/',
        views.newsletter_delete,
        name='newsletter_delete'
    ),
    path(
        'reader/newsletters/',
        views.reader_newsletters,
        name='reader_newsletters'
    ),

    # Publisher web CRUD
    path('publishers/', views.publisher_list, name='publisher_list'),
    path(
        'publishers/create/',
        views.publisher_create,
        name='publisher_create'
    ),
    path(
        'publishers/<int:publisher_id>/edit/',
        views.publisher_update,
        name='publisher_update'
    ),
    path(
        'publishers/<int:publisher_id>/delete/',
        views.publisher_delete,
        name='publisher_delete'
    ),

    # Journalist list and subscriptions
    path('journalists/', views.journalist_list, name='journalist_list'),
    path(
        'journalists/<int:journalist_id>/subscribe/',
        views.subscribe_journalist,
        name='subscribe_journalist'
    ),
    path(
        'publishers/<int:publisher_id>/subscribe/',
        views.subscribe_publisher,
        name='subscribe_publisher'
    ),

    # API routes
    path('api/', include(router.urls)),
    path(
        'api/approved/',
        views.approved_article_log_api,
        name='approved_article_log_api'
    ),
]