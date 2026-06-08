import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Task, Category


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpass123')


@pytest.fixture
def logged_in_client(client, user):
    client.login(username='testuser', password='testpass123')
    return client


@pytest.fixture
def category(user, db):
    return Category.objects.create(name='Work', user=user)


@pytest.fixture
def task(user, category, db):
    return Task.objects.create(
        title='Test Task',
        description='A test description',
        user=user,
        category=category,
        priority='medium',
    )


# --- Auth tests ---

@pytest.mark.django_db
def test_register_new_user(client):
    response = client.post(reverse('register'), {
        'username': 'newuser',
        'password1': 'StrongPass99!',
        'password2': 'StrongPass99!',
    })
    assert response.status_code == 302
    assert User.objects.filter(username='newuser').exists()


@pytest.mark.django_db
def test_login_valid_user(client, user):
    response = client.post(reverse('login'), {
        'username': 'testuser',
        'password': 'testpass123',
    })
    assert response.status_code == 302


@pytest.mark.django_db
def test_login_invalid_credentials(client):
    response = client.post(reverse('login'), {
        'username': 'nobody',
        'password': 'wrongpass',
    })
    assert response.status_code == 200


@pytest.mark.django_db
def test_unauthenticated_redirected_to_login(client):
    response = client.get(reverse('task_list'))
    assert response.status_code == 302
    assert '/login/' in response['Location']


# --- Task CRUD tests ---

@pytest.mark.django_db
def test_task_list_returns_200(logged_in_client):
    response = logged_in_client.get(reverse('task_list'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_task(logged_in_client, user):
    response = logged_in_client.post(reverse('task_create'), {
        'title': 'New Task',
        'description': 'Some description',
        'priority': 'high',
        'completed': False,
    })
    assert response.status_code == 302
    assert Task.objects.filter(title='New Task', user=user).exists()


@pytest.mark.django_db
def test_edit_task(logged_in_client, task):
    response = logged_in_client.post(reverse('task_edit', args=[task.pk]), {
        'title': 'Updated Title',
        'description': task.description,
        'priority': 'low',
        'completed': True,
    })
    assert response.status_code == 302
    task.refresh_from_db()
    assert task.title == 'Updated Title'
    assert task.completed is True


@pytest.mark.django_db
def test_delete_task(logged_in_client, task):
    response = logged_in_client.post(reverse('task_delete', args=[task.pk]))
    assert response.status_code == 302
    assert not Task.objects.filter(pk=task.pk).exists()


@pytest.mark.django_db
def test_toggle_task_completion(logged_in_client, task):
    assert task.completed is False
    logged_in_client.get(reverse('task_toggle', args=[task.pk]))
    task.refresh_from_db()
    assert task.completed is True


# --- Category tests ---

@pytest.mark.django_db
def test_create_category(logged_in_client, user):
    response = logged_in_client.post(reverse('category_list'), {'name': 'Personal'})
    assert response.status_code == 302
    assert Category.objects.filter(name='Personal', user=user).exists()


@pytest.mark.django_db
def test_cannot_access_other_users_task(client, db):
    owner = User.objects.create_user(username='owner', password='pass123')
    other = User.objects.create_user(username='other', password='pass123')
    task = Task.objects.create(title='Private', user=owner, priority='low')

    client.login(username='other', password='pass123')
    response = client.get(reverse('task_edit', args=[task.pk]))
    assert response.status_code == 404

