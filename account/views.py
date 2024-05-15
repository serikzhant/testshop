from .forms import UserCreateForm, UserLoginForm, UserUpdateForm
from django.contrib import messages
from django.contrib.auth import login, authenticate, get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django_email_verification import send_email


User = get_user_model()

# Registration


def register_user(request):

    if request.method == 'POST':
        form = UserCreateForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user_email = form.cleaned_data['email']
            user_username = form.cleaned_data['username']
            user_password = form.cleaned_data['password1']

            # Create new user
            user = User.objects.create_user(
                username=user_username, email=user_email, password=user_password)

            user.is_active = False
            send_email(user)

            return redirect('/account/email/email-verification')
    else:
        form = UserCreateForm()
    return render(request, 'account/registration/register.html', {'form': form})


def login_user(request):

    form = UserLoginForm()

    if request.user.is_authenticated:
        return redirect('shop:products')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('account:dashboard')
        else:
            messages.info(request, 'Username or Password is incorrect')
            return redirect('account:login')
    context = {'form': form}

    return render(request, 'account/login/login.html', context)


def logout_user(request):
    logout(request)
    return redirect('shop:products')


@login_required(login_url='account:login')
def dashboard_user(request):

    return render(request, 'account/dashboard/dashboard.html')


@login_required(login_url='account:login')
def profile_user(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('account:dashboard')
    else:
        form = UserUpdateForm(instance=request.user)

    context = {
        'form': form
    }
    return render(request, 'account/dashboard/profile-management.html', context)


@login_required(login_url='account:login')
def delete_user(request):
    user = User.objects.get(id=request.user.id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Account deleted successfully')
        return redirect('shop:products')
    return render(request, 'account/dashboard/account-delete.html')
