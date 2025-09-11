import pytest
from django.urls import reverse
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_login_view_get(client):
    response = client.get(reverse('login'))
    assert response.status_code == 200
    assert 'registration/login.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_login_view_post(client):
    User.objects.create_user(username='testuser', password='testpassword')
    response = client.post(reverse('login'), {
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 302  

@pytest.mark.django_db
def test_login_view_post_invalid(client):
    response = client.post(reverse('login'), {
        'username': 'nonexistent',
        'password': 'wrongpassword'
    })
    assert response.status_code == 200  
