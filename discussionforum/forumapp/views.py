from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse   
from django.contrib.auth import login, authenticate  
from django.contrib.sites.shortcuts import get_current_site  
from django.utils.encoding import force_bytes, force_str 
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  
from django.template.loader import render_to_string  
from .token import account_activation_token  
from django.contrib.auth.models import User  
from django.core.mail import EmailMessage  
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import auth

from .models import Profile,Post,Comment,Category
# Create your views here.
@login_required(login_url='signin')
def home(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile, created = Profile.objects.get_or_create(user=user_object)
    category=Category.objects.all()
    
    
    context={
        'category':category,
        "user_profile":user_profile,
    }
    return render(request,"home.html",context)
def signin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:  # Check if the user is active
                auth.login(request, user)
                return redirect('home')  # Redirect to the 'index' page
            else:
                messages.error(request, 'Your account is not active.')
                return redirect('signin')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('signin')
    else:
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return render(request, 'register/signin.html')

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['confirm_password']
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email is taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.is_active = False  # Set the user's status to inactive
                user.save()

                current_site = get_current_site(request)
                mail_subject = 'Activation link has been sent to your email id'
                message = render_to_string('acc_active_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                email = EmailMessage(
                    mail_subject, message, to=[email]
                )
                email.send()
                # user_login = authenticate(username=username, password=password)
                login(request, user)
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()

                return HttpResponse('Please confirm your email address to complete the registration')  # Redirect to the 'home' page after successful signup
        else:
            messages.info(request, "Passwords do not match")
            return redirect('signup')
    else:
        return render(request, 'register/signup.html')

def activate(request, uidb64, token):  
    User = get_user_model()  
    try:  
        uid = force_str(urlsafe_base64_decode(uidb64))  
        user = User.objects.get(pk=uid)  
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):  
        user = None  
    if user is not None and account_activation_token.check_token(user, token):  
        user.is_active = True  
        user.save()  
        return redirect('home')  
    else:  
        return HttpResponse('Activation link is invalid!')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')