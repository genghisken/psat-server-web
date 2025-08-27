from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.contrib import auth, messages
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.decorators import login_required, user_passes_test
import logging

from accounts.models import UserProfile
from accounts.utils import needs_to_change_password

logger = logging.getLogger(__name__)


class LoginForm(forms.Form):
    """LoginForm.
    """

    username = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'size': '50', 'class': 'form-control'}
        )
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={'size': '50', 'class': 'form-control'}
        )
    )


def loginView(request):
    """login.

    Args:
        request:
    """
    auth.logout(request)
    form = LoginForm()
    return render(request, 'login.html', {'form': form})


def authView(request):
    """authView.

    Args:
        request:
    """
    # Although we picked up the "next" parameter via GET in our template,
    # we submitted it via POST.
    next = request.POST.get('next', '')

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        # Expire the login session after 1 day.
        # 2017-11-28 KWS Changed expiry to 30 days.
        # 1 day expiry too irritating.
        request.session.set_expiry(30 * 86400)
        auth.login(request, user)
        try:
            if user.profile.password_unuseable_fl:
                return redirect('change_password')
        except AttributeError:
            logger.warning(f'User {user} has no profile.')
        
        if next == '':
            return redirect('home')
        else:
            return redirect(next)

    else:
        return redirect('invalid')


def loggedin(request):
    """loggedin.

    Args:
        request:
    """
    return render(request, 'loggedin.html',
                  {'full_name': request.user.username})


def invalidLogin(request):
    """invalidLogin.

    Args:
        request:
    """
    return render(request, 'invalid_login.html')


def logoutView(request):
    """logout.

    Args:
        request:
    """
    auth.logout(request)
    return render(request, 'logout.html')


def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


class AtlasPasswordChangeForm(PasswordChangeForm):
    """AtlasPasswordChangeForm.
    """
    error_messages = {
        **PasswordChangeForm.error_messages,
        'password_old_same_new': (
            "The new password cannot be the same as the old password."
        ),
        'old_password_incorrect': "The old password is not correct.",
    }

    def clean_new_password1(self):
        """ 
        Further checking on old password to ensure it is not the same as the 
        new password.
        """
        new_password1 = self.cleaned_data['new_password1']
        try:
            old_password = self.cleaned_data['old_password']
        except KeyError:
            # This is a new password change form, so we don't have an old
            # password to check against.
            raise forms.ValidationError(
                self.error_messages['old_password_incorrect'],
                code='old_password_incorrect',
            )
        
        if old_password == new_password1:
            raise forms.ValidationError(
                self.error_messages['password_old_same_new'],
                code='password_old_same_new',
            )
        return new_password1


class AtlasPasswordChangeView(auth_views.PasswordChangeView):
    """AtlasPasswordChangeView.
    """
    form_class = AtlasPasswordChangeForm
    template_name = 'change_password.html'
    
    def form_valid(self, form):
        # Unset the password_unuseable flag in the user profile
        try:
            form.user.profile.password_unuseable_fl = False
            form.user.profile.save()
        except AttributeError:
            logger.warning(f'User {form.user} has no profile.')
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        try:
            context_data['password_unuseable_fl'] = (
                self.request.user.profile.password_unuseable_fl
            )
        except AttributeError:
            logger.warning(f'User {self.request.user} has no profile.')
            context_data['password_unuseable_fl'] = False
        return context_data


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='invalid')
def create_user(request):
    """
    Create a new user with profile settings.
    Only accessible by admin users.
    """
    from accounts.forms import CreateUserForm
    from accounts.models import UserProfile, GroupProfile
    from django.contrib.auth.models import User
    from django.contrib import messages
    
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            try:
                # Create the user
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    password='atlas'
                )
                
                user.save()

                if form.cleaned_data.get('has_write_access'):
                    # Grant write access if the checkbox is checked
                    permission = Permission.objects.get(
                        codename='has_write_access'
                    )
                    user.user_permissions.add(
                        permission
                    )
                
                # Add user to selected group
                group = form.cleaned_data['group']
                user.groups.add(group)
                
                # Create or update user profile
                profile, created = UserProfile.objects.get_or_create(user=user)
                # Temp password must be changed by user
                profile.password_unuseable_fl = True 
                profile.save()
                image = form.cleaned_data.get('image')
                if image:
                    profile.image = image
                    profile.save()
                
                messages.success(
                    request,
                    f'User {user.username} created successfully!'
                )
                
                # Clear form for next user creation
                form = CreateUserForm()
                
            except Exception as e:
                messages.error(request, f'Error creating user: {str(e)}')
                
    else:
        form = CreateUserForm()
    
    # Get group information for display
    groups_info = []
    for group in Group.objects.all():
        try:
            group_profile = GroupProfile.objects.get(group=group)
            groups_info.append({
                'group': group,
                'token_expiration': group_profile.token_expiration_time,
                'api_write_access': group_profile.api_write_access,
                'description': group_profile.description
            })
        except GroupProfile.DoesNotExist:
            groups_info.append({
                'group': group,
                'token_expiration': 'Not set',
                'api_write_access': False,
                'description': 'No profile configured'
            })
    
    context = {
        'form': form,
        'groups_info': groups_info,
        'title': 'Create New User'
    }
    
    return render(request, 'create_user.html', context)


@user_passes_test(
    lambda u: not needs_to_change_password(u),
    login_url='change_password'
)
@login_required
def change_profile_image(request):
    """Change the user's profile image.
    
    Args:
        request: The HTTP request object.
    """
    from accounts.forms import ChangeProfileImageForm
    
    if request.method == 'POST':
        form = ChangeProfileImageForm(request.POST, request.FILES)
        if form.is_valid():
            profile = UserProfile.objects.get(user=request.user)
            image = form.cleaned_data.get('image')
            if image:
                profile.image = image
                profile.save()
            messages.success(request, 'Profile image updated successfully!')
            return redirect('home')
    else:
        form = ChangeProfileImageForm()
    
    return render(request, 'change_profile_image.html', {'form': form})
