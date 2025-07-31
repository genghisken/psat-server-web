"""
Tests for the create user functionality.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from accounts.models import UserProfile, GroupProfile
from accounts.forms import CreateUserForm
import os

moduleDirectory = os.path.dirname(os.path.realpath(__file__))


class CreateUserViewTest(TestCase):
    """Tests for the create user view."""
    
    def setUp(self):
        """Set up test data."""
        # Create a regular user
        self.regular_user = User.objects.create_user(
            username='regular',
            password='testpass123'
        )
        
        # Create an admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_staff=True
        )
        
        # Create a test group with profile
        self.test_group = Group.objects.create(name='test_group')
        self.group_profile = GroupProfile.objects.create(
            group=self.test_group,
            api_write_access=True,
            description='Test group for API access'
        )
        
        self.client = Client()
        self.create_user_url = reverse('create_user')
    
    def test_access_denied_for_anonymous_user(self):
        """Test that anonymous users cannot access create user page."""
        response = self.client.get(self.create_user_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_access_denied_for_regular_user(self):
        """Test that regular users cannot access create user page."""
        self.client.login(username='regular', password='testpass123')
        response = self.client.get(self.create_user_url)
        self.assertEqual(response.status_code, 302)  # Redirect to invalid page
    
    def test_access_granted_for_admin_user(self):
        """Test that admin users can access create user page."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(self.create_user_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New User')
    
    def test_create_user_form_displays_groups(self):
        """Test that the form displays group information."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(self.create_user_url)
        self.assertContains(response, 'test_group')
        self.assertContains(response, 'Test group for API access')
    
    def test_create_user_success(self):
        """Test successful user creation."""
        self.client.login(username='admin', password='testpass123')
        
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'group': self.test_group.id,
        }

        img_file = open(moduleDirectory + '/test-image.jpg', 'rb')
        form_data['image'] = img_file
        
        response = self.client.post(self.create_user_url, form_data)
        self.assertEqual(response.status_code, 200)
        
        # Check that user was created
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.email, 'newuser@example.com')
        self.assertEqual(new_user.first_name, 'New')
        self.assertEqual(new_user.last_name, 'User')
        self.assertTrue(new_user.has_usable_password())
        
        # Check that user is in the correct group
        self.assertTrue(new_user.groups.filter(id=self.test_group.id).exists())
        
        # Check that user profile was created with correct settings
        profile = UserProfile.objects.get(user=new_user)
        self.assertTrue(profile.password_unuseable_fl)
    
    def test_create_user_duplicate_username(self):
        """Test that creating a user with duplicate username fails."""
        self.client.login(username='admin', password='testpass123')
        
        form_data = {
            'username': 'regular',  # Already exists
            'email': 'different@example.com',
            'first_name': 'Different',
            'last_name': 'User',
            'group': self.test_group.id,
        }
        
        response = self.client.post(self.create_user_url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'A user with this username already exists'
        )

    def test_create_user_duplicate_email(self):
        """Test that creating a user with duplicate email fails."""
        # Create a user with an email first
        User.objects.create_user(
            username='emailuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.client.login(username='admin', password='testpass123')
        
        form_data = {
            'username': 'newuser',
            'email': 'test@example.com',  # Already exists
            'first_name': 'New',
            'last_name': 'User',
            'group': self.test_group.id,
        }
        
        response = self.client.post(self.create_user_url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A user with this email already exists')


class CreateUserFormTest(TestCase):
    """Tests for the CreateUserForm."""
    
    def setUp(self):
        """Set up test data."""
        self.test_group = Group.objects.create(name='test_group')
    
    def test_form_valid_data(self):
        """Test form with valid data."""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'group': self.test_group.id,
            'image': None  # No image uploaded
        }
        
        form = CreateUserForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_email(self):
        """Test form with invalid email."""
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'first_name': 'Test',
            'last_name': 'User',
            'group': self.test_group.id,
        }
        
        form = CreateUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_form_missing_required_fields(self):
        """Test form with missing required fields."""
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
        }
        
        form = CreateUserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('group', form.errors)