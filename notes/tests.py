from django.test import TestCase
from django.urls import reverse
from .utils import add


class AddFunctionTestCase(TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)


class HomePageTestCase(TestCase):
    def test_home_page_contains_homepage_text(self):
        response = self.client.get(reverse('notes:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Homepage')


class NotesTestCase(TestCase):
    def test_notes_can_be_created(self):
        # Act
        response = self.client.post(reverse('notes:add'), {
            'title': 'Django Course1',
            'description': 'Complete course with urls, templates, models, etc'
        })

        # Assert
        # Redirect after successful creation
        self.assertEqual(response.status_code, 302)

        # Follow redirect and check the note appears
        response = self.client.get(response.url)
        self.assertContains(response, 'Django Course')

    def test_error_occurs_if_description_is_less_than_10_chars_long(self):
        # Act
        response = self.client.post(reverse('notes:add'), {
            'title': 'Django Course',
            'description': 'dj'
        })

        # Assert
        # Should return to form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 'Description must be at least 10 characters long')