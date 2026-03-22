from django.test import TestCase
from django.urls import reverse
from .models import Note
from .utils import add


class AddFunctionTestCase(TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)


class HomePageTestCase(TestCase):
    def test_home_page_contains_homepage_text(self):
        response = self.client.get(reverse('notes:index'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Homepage')


class NotesTestCase(TestCase):
    def test_notes_can_be_created(self):
        response = self.client.post(
            reverse('notes:add'),
            {
                'title': 'Django Course',
                'description': 'Complete course with urls, templates, models, etc',
            },
            follow=True,
            secure=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.redirect_chain), 1)
        self.assertEqual(Note.objects.count(), 1)
        self.assertTrue(Note.objects.filter(title='Django Course').exists())

        index_response = self.client.get(reverse('notes:index'), follow=True, secure=True)
        self.assertContains(index_response, 'Django Course')

    def test_error_occurs_if_description_is_less_than_10_chars_long(self):
        response = self.client.post(
            reverse('notes:add'),
            {
                'title': 'Django Course',
                'description': 'dj',
            },
            follow=True,
            secure=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Description must be at least 10 characters long')
        self.assertEqual(Note.objects.count(), 0)