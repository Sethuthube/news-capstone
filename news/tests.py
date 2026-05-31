from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Article, CustomUser, Newsletter, Publisher


class NewsAPITestCase(APITestCase):
    """
    Tests for the news application REST API.
    """

    def setUp(self):
        """
        Create test users, publisher, article, and newsletter.
        """

        self.reader = CustomUser.objects.create_user(
            username='reader_test',
            email='reader@example.com',
            password='Testpass123!',
            role=CustomUser.READER
        )

        self.editor = CustomUser.objects.create_user(
            username='editor_test',
            email='editor@example.com',
            password='Testpass123!',
            role=CustomUser.EDITOR
        )

        self.journalist = CustomUser.objects.create_user(
            username='journalist_test',
            email='journalist@example.com',
            password='Testpass123!',
            role=CustomUser.JOURNALIST
        )

        self.publisher = Publisher.objects.create(
            name='Test Publisher',
            description='A test publisher.'
        )

        self.publisher.journalists.add(self.journalist)
        self.reader.subscribed_journalists.add(self.journalist)
        self.reader.subscribed_publishers.add(self.publisher)

        self.approved_article = Article.objects.create(
            title='Approved Article',
            content='This approved article should be visible.',
            author=self.journalist,
            publisher=self.publisher,
            approved=True
        )

        self.unapproved_article = Article.objects.create(
            title='Unapproved Article',
            content='This article is waiting for editor approval.',
            author=self.journalist,
            publisher=self.publisher,
            approved=False
        )

        self.newsletter = Newsletter.objects.create(
            title='Weekly Newsletter',
            description='A test newsletter.',
            author=self.journalist
        )
        self.newsletter.articles.add(self.approved_article)

    def test_authenticated_reader_can_view_articles(self):
        """
        Reader should be able to view approved articles.
        """

        self.client.force_authenticate(user=self.reader)

        response = self.client.get('/api/articles/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], 'Approved Article')

    def test_reader_can_view_subscribed_articles(self):
        """
        Reader should receive articles from subscribed journalists/publishers.
        """

        self.client.force_authenticate(user=self.reader)

        response = self.client.get('/api/articles/subscribed/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Approved Article')

    def test_unauthenticated_user_cannot_access_articles(self):
        """
        Unauthenticated users should not access protected article API.
        """

        response = self.client.get('/api/articles/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_journalist_can_create_article(self):
        """
        Journalist should be able to create an article.
        """

        self.client.force_authenticate(user=self.journalist)

        data = {
            'title': 'Journalist Created Article',
            'content': 'This article was created through the API.',
            'publisher': self.publisher.id,
        }

        response = self.client.post('/api/articles/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Journalist Created Article')
        self.assertFalse(response.data['approved'])

    def test_reader_cannot_create_article(self):
        """
        Reader should not be allowed to create an article.
        """

        self.client.force_authenticate(user=self.reader)

        data = {
            'title': 'Reader Created Article',
            'content': 'Readers should not be allowed to create articles.',
            'publisher': self.publisher.id,
        }

        response = self.client.post('/api/articles/', data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_editor_can_approve_article(self):
        """
        Editor should be able to approve an article.
        """

        self.client.force_authenticate(user=self.editor)

        url = f'/api/articles/{self.unapproved_article.id}/approve/'
        response = self.client.post(url)

        self.unapproved_article.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.unapproved_article.approved)

    def test_editor_can_delete_article(self):
        """
        Editor should be able to delete an article.
        """

        self.client.force_authenticate(user=self.editor)

        url = f'/api/articles/{self.unapproved_article.id}/'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_newsletter_list_works(self):
        """
        Authenticated users should be able to view newsletters.
        """

        self.client.force_authenticate(user=self.reader)

        response = self.client.get('/api/newsletters/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], 'Weekly Newsletter')
