from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
import requests
from .models import User
from notifications.utils import send_group_notification, send_user_notification

@login_required
def discord_link(request):
    url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={settings.DISCORD_CLIENT_ID}"
        f"&redirect_uri={settings.DISCORD_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=identify%20email"
    )
    return redirect(url)

@login_required
def discord_callback(request):
    code = request.GET.get('code')
    if not code:
        messages.error(request, "No code returned from Discord.")
        return redirect('profile')
    data = {
        'client_id': settings.DISCORD_CLIENT_ID,
        'client_secret': settings.DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.DISCORD_REDIRECT_URI,
        'scope': 'identify email',
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    token_resp = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
    if token_resp.status_code != 200:
        messages.error(request, "Failed to get Discord token.")
        return redirect('profile')
    access_token = token_resp.json().get('access_token')
    user_resp = requests.get('https://discord.com/api/users/@me', headers={'Authorization': f'Bearer {access_token}'})
    if user_resp.status_code != 200:
        messages.error(request, "Failed to fetch Discord user info.")
        return redirect('profile')
    discord_id = user_resp.json().get('id')
    request.user.discord_id = discord_id
    request.user.save()
    messages.success(request, "Discord account linked successfully!")
    return redirect('profile')

def home_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    return redirect('login')

def custom_login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_approved:
                messages.error(request, 'Your email is verified, but your account is pending admin approval. You will be notified when approved.')
                return render(request, 'registration/login.html', {'form': form})
            login(request, user)
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('profile')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def profile_edit_view(request):
    from .forms import ProfileEditForm
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile picture updated successfully.')
            return redirect('dashboard')
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'account/profile_edit.html', {'form': form, 'user': request.user})

@login_required
def profile_view(request):
    return render(request, 'account/profile.html', {'user': request.user})

def registration_view(request):
    from .forms import UserRegistrationForm
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            admins = User.objects.filter(is_admin=True)
            message = f"A new user, {user.username}, has registered and is awaiting approval."
            send_group_notification(admins, message)

            messages.success(request, 'Your application has been submitted. You will be notified when it is approved.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'account/register.html', {'form': form})

@staff_member_required
def admin_approval_queue(request):
    pending_users = User.objects.filter(is_approved=False, is_active=False)
    return render(request, 'account/admin_approval.html', {'users': pending_users})

@staff_member_required
def approve_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = True
    user.is_approved = True
    user.save()
    send_user_notification(user, "Your account has been approved!")
    messages.success(request, f"User {user.email} has been approved.")
    return redirect('admin_approval_queue')

@staff_member_required
def reject_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    messages.warning(request, f"User {user.email} has been rejected.")
    return redirect('admin_approval_queue')

@staff_member_required
def analytics_view(request):
    from events.models import Event
    from trading.models import Trade

    total_users = User.objects.count()
    approved_users = User.objects.filter(is_approved=True).count()
    total_events = Event.objects.count()
    total_trades = Trade.objects.count()

    data = {
        'total_users': total_users,
        'approved_users': approved_users,
        'total_events': total_events,
        'total_trades': total_trades,
    }

    return JsonResponse(data)

