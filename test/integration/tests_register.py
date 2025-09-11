# tests.py
import pytest
from django.urls import reverse
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_register_view_get(client):
    response = client.get(reverse('home:registro'))
    assert response.status_code == 200
    assert 'registration/registro.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_register_view_post(client):
    response = client.post(reverse('home:registro'), {
        'username': 'testuser',
        'password1': 'testpassword',
        'password2': 'testpassword'
    })
    assert response.status_code == 302  # Redirige después del registro
    assert User.objects.count() == 1

@pytest.mark.django_db
def test_register_view_post_invalid(client):
    response = client.post(reverse('home:registro'), {
        'username': 'testuser',
        'password1': 'testpassword',
        'password2': 'wrongpassword'
    })
    assert response.status_code == 200  # La página de registro se vuelve a cargar con errores
    assert User.objects.count() == 0
