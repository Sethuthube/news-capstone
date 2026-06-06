from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from rest_framework.test import APIClient

from .models import Article, ApprovedArticleLog, CustomUser, Newsletter, Publisher


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='newsapp@example.com'
)
class NewsApplicationTests(TestCase):
    """
    Automated tests for the News Application capstone project.

    These tests cover:
    - Role-based API access.
    - Reader subscribed article filtering.
    - Journalist article creation.
    - Editor approval and delete permissions.
    - Newsletter behaviour.
    - Approval notification/email logic.
    """

    def setUp(self):
        self.client = APIClient()

        self.reader = CustomUser.objects.create_user(
            username='reader_test',
            email='reader_unit@example.com',
            password='Testpass123!',
            role='reader'
        )

        self.journalist = CustomUser.objects.create_user(
            username='journalist_test',
            email='journalist_unit@example.com',
            password='Testpass123!',
            role='journalist'
        )

        self.other_journalist = CustomUser.objects.create_user(
            username='other_journalist',
            email='other_journalist_unit@example.com',
            password='Testpass123!',
            role='journalist'
        )

        self.editor = CustomUser.objects.create_user(
            username='editor_test',
            email='editor_unit@example.com',
            password='Testpass123!',
            role='editor'
        )

        self.publisher = Publisher.objects.create(
            name='Test Publisher',
            description='Publisher used for automated tests.'
        )

        self.publisher.journalists.add(self.journalist)
        self.publisher.editors.add(self.editor)

        self.approved_article = Article.objects.create(
            title='Approved Article',
            content='This approved article should be visible to readers.',
            author=self.journalist,
            publisher=self.publisher,
            approved=True
        )

        self.unapproved_article = Article.objects.create(
            title='Pending Article',
            content='This article is waiting for editor approval.',
            author=self.journalist,
            publisher=self.publisher,
            approved=False
        )

        self.other_article = Article.objects.create(
            title='Other Journalist Article',
            content='This article belongs to another journalist.',
            author=self.other_journalist,
            approved=True
        )

    def authenticate(self, user):
        """
        Force authenticate an API request as a specific user.
        """
        self.client.force_authenticate(user=user)

    def test_reader_can_only_retrieve_approved_articles(self):
        self.authenticate(self.reader)

        response = self.client.get('/api/articles/')

        self.assertEqual(response.status_code, 200)

        titles = [article['title'] for article in response.data]

        self.assertIn('Approved Article', titles)
        self.assertIn('Other Journalist Article', titles)
        self.assertNotIn('Pending Article', titles)

    def test_reader_can_retrieve_only_subscribed_content(self):
        self.reader.subscribed_publishers.add(self.publisher)
        self.reader.subscribed_journalists.add(self.journalist)

        self.authenticate(self.reader)

        response = self.client.get('/api/articles/subscribed/')

        self.assertEqual(response.status_code, 200)

        titles = [article['title'] for article in response.data]

        self.assertIn('Approved Article', titles)
        self.assertNotIn('Other Journalist Article', titles)
        self.assertNotIn('Pending Article', titles)

    def test_journalist_can_create_article(self):
        self.authenticate(self.journalist)

        payload = {
            'title': 'Journalist Created Article',
            'content': 'This article was created by a journalist through the API.',
            'publisher': self.publisher.id,
        }

        response = self.client.post('/api/articles/', payload, format='json')

        self.assertEqual(response.status_code, 201)

        article = Article.objects.get(title='Journalist Created Article')

        self.assertEqual(article.author, self.journalist)
        self.assertFalse(article.approved)

    def test_reader_cannot_create_article(self):
        self.authenticate(self.reader)

        payload = {
            'title': 'Reader Should Not Create This',
            'content': 'Readers should not be allowed to create articles.',
            'publisher': self.publisher.id,
        }

        response = self.client.post('/api/articles/', payload, format='json')

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            Article.objects.filter(title='Reader Should Not Create This').exists()
        )

    def test_editor_can_approve_article(self):
        self.reader.subscribed_publishers.add(self.publisher)

        self.authenticate(self.editor)

        response = self.client.post(
            f'/api/articles/{self.unapproved_article.id}/approve/'
        )

        self.assertEqual(response.status_code, 200)

        self.unapproved_article.refresh_from_db()

        self.assertTrue(self.unapproved_article.approved)
        self.assertTrue(
            ApprovedArticleLog.objects.filter(
                article=self.unapproved_article
            ).exists()
        )

    def test_reader_cannot_approve_article(self):
        self.authenticate(self.reader)

        response = self.client.post(
            f'/api/articles/{self.unapproved_article.id}/approve/'
        )

        self.assertEqual(response.status_code, 403)

        self.unapproved_article.refresh_from_db()

        self.assertFalse(self.unapproved_article.approved)

    def test_editor_can_delete_article(self):
        self.authenticate(self.editor)

        response = self.client.delete(
            f'/api/articles/{self.approved_article.id}/'
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Article.objects.filter(id=self.approved_article.id).exists()
        )

    def test_reader_cannot_delete_article(self):
        self.authenticate(self.reader)

        response = self.client.delete(
            f'/api/articles/{self.approved_article.id}/'
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Article.objects.filter(id=self.approved_article.id).exists()
        )

    def test_newsletter_can_be_created_by_journalist(self):
        self.authenticate(self.journalist)

        payload = {
            'title': 'Weekly Test Newsletter',
            'description': 'Newsletter created during automated testing.',
            'articles': [self.approved_article.id],
        }

        response = self.client.post('/api/newsletters/', payload, format='json')

        self.assertEqual(response.status_code, 201)

        newsletter = Newsletter.objects.get(title='Weekly Test Newsletter')

        self.assertEqual(newsletter.author, self.journalist)
        self.assertIn(self.approved_article, newsletter.articles.all())

    def test_approval_sends_email_to_subscribed_reader(self):
        self.reader.subscribed_publishers.add(self.publisher)

        self.authenticate(self.editor)

        response = self.client.post(
            f'/api/articles/{self.unapproved_article.id}/approve/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]

        self.assertIn('New approved article', email.subject)
        self.assertIn(self.reader.email, email.to)

    def test_duplicate_email_is_not_allowed(self):
        duplicate_user = CustomUser(
            username='duplicate_reader',
            email='reader_unit@example.com',
            role='reader'
        )

        with self.assertRaises(Exception):
            duplicate_user.save()
