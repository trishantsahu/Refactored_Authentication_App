from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from UserAuthentication.decorators import anonymous_required, login_required

CustomUser = get_user_model()


def _dummy_view(request):
    return HttpResponse("ok")


def _attach_session_and_messages(request):
    from django.contrib.sessions.middleware import SessionMiddleware
    from django.contrib.messages.middleware import MessageMiddleware

    SessionMiddleware(lambda r: None).process_request(request)
    request.session.save()
    MessageMiddleware(lambda r: None).process_request(request)


class LoginRequiredDecoratorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(
            username='decoduser', email='deco@barc.gov.in',
            password='Tr1cky&UnusualPass!9', employee_id='33333',
        )

    def test_redirects_anonymous_user_to_login(self):
        request = self.factory.get('/home/')
        request.user = AnonymousUser()
        _attach_session_and_messages(request)

        response = login_required(_dummy_view)(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
        # next= should be preserved so the user lands back on /home/ after login
        self.assertIn('next=', response.url)

    def test_allows_authenticated_user_through(self):
        request = self.factory.get('/home/')
        request.user = self.user
        _attach_session_and_messages(request)

        response = login_required(_dummy_view)(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")


class AnonymousRequiredDecoratorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(
            username='anonuser', email='anon@barc.gov.in',
            password='Tr1cky&UnusualPass!9', employee_id='44444',
        )

    def test_redirects_authenticated_user_away(self):
        request = self.factory.get('/login/')
        request.user = self.user

        response = anonymous_required(redirect_to='home')(_dummy_view)(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/home/')

    def test_allows_anonymous_user_through(self):
        request = self.factory.get('/login/')
        request.user = AnonymousUser()

        response = anonymous_required(redirect_to='home')(_dummy_view)(request)
        self.assertEqual(response.status_code, 200)
