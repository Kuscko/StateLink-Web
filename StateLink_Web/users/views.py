from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout

# Create your views here.

# Default Pages
def home_view(request):
    return render(request, 'home.html') # Render the home page

# Authentication Pages
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST) # Create a new user
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home') # Redirect to home page after successful registration
    else:
        form = UserCreationForm() # Render the registration form
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)  # Use AuthenticationForm for login
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirect to home page after successful login
        else:
            # Handle invalid login attempts
            return render(request, 'login.html', {'form': form, 'error': 'Invalid username and password'}, status=401)
    else:
        form = AuthenticationForm()  # Pre-fill the form with empty values
    return render(request, 'login.html', {'form': form})  # Always pass the form to the template

def logout_view(request):
    logout(request)
    return redirect('login') # Redirect to login page after logout