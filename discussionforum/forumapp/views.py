from django.shortcuts import render,redirect,get_object_or_404
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
from itertools import chain

from .models import Profile,Post,Comment,Category,DiscussionThread
from .form import PostForm 
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


@login_required(login_url='signin')
def posts_by_category(request, category):
    posts = Post.objects.filter(category__name=category)  # Retrieve posts based on the category
    category_name = Category.objects.get(name=category)  # Retrieve the category object
    
    # Retrieve comments for each post
    all_comments = []
    for post in posts:
        post_comments = Comment.objects.filter(post=post).all()[:2]
        all_comments.append(post_comments)
    post_count = len(all_comments)  # Count the total comments

    post_count = len(list(chain.from_iterable(all_comments)))  # Flatten list of lists to a single list

    context = {
    "category": category_name,
    "posts": posts,
    "comments": all_comments,  
    "post_count": post_count
    }
    return render(request, "posts/posts.html", context)
@login_required(login_url='signin')
def detail(request,pk):
    post = get_object_or_404(Post, id=pk)
    post_comments = {}
    post_comments = Comment.objects.filter(post=post).all()
    comment=post_comments
    # post_count=post_comments.count()
    context={
        "post":post,
        "comment":comment
    }
    return render(request, "posts/detail.html" ,context)

@login_required
def upload_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data['is_new_thread']:
                # Create new thread and first post
                thread = DiscussionThread.objects.create(title=form.cleaned_data['title'], creator=request.user)
                post = form.save(commit=False)
                post.thread = thread
                post.creator = request.user
                post.save()
                return redirect('detail', pk=thread.pk)
            else:
                # Update existing post
                post = form.save(commit=False)
                post.creator = request.user
                post.save()
                return redirect('detail', pk=post.pk)
    else:
        form = PostForm()
    context = {'form': form}
    return render(request, 'posts/upload.html', context)

@login_required(login_url='signin')
def update_post(request, pk):
    # Retrieve the post object using its UUID primary key
    post = get_object_or_404(Post, id=pk)

    # Ensure the user is authorized to edit the post
    if post.creator != request.user:
        return redirect('detail', pk=pk)  
    if request.method == 'GET':
        
        form = PostForm(instance=post)
        context = {'form': form, 'post': post}
        return render(request, 'posts/update.html', context)
    elif request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)  
        if form.is_valid():
            form.save()
            return redirect('detail', pk=post.pk)  
        else:
            context = {'form': form, 'post': post}
            return render(request, 'posts/update.html', context)
    
    return render(request, 'posts/update.html', context)

@login_required(login_url='signin')
def delete_post(request, pk):
    post = get_object_or_404(Post, id=pk)

    if post.creator != request.user:
        messages.error(request, "You are not authorized to delete this post.")
        return redirect('detail', pk=pk)

    post.delete()
    messages.success(request, "Post successfully deleted.")
    return redirect('posts_by_category', category_name=post.category.name)  

def signin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:  
                auth.login(request, user)
                return redirect('home')  
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
