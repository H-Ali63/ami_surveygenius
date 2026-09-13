from django.test import TestCase


class SessionTimeoutMiddlewareTests(TestCase):
    def test_login_page_is_available_without_redirecting(self):
        response = self.client.get('/login')

        self.assertEqual(response.status_code, 200)

    def test_protected_pages_redirect_to_login_with_next_param(self):
        response = self.client.get('/search', follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login?next=/search', fetch_redirect_response=False)
