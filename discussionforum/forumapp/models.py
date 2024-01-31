from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime
from django.core.exceptions import PermissionDenied

User=get_user_model()
# Create your models here.
class Profile(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    id_user=models.IntegerField()
    bio=models.TextField(blank=True)
    Profile_img=models.ImageField(upload_to='profile_images',default='blank-profile-picture.png')
    
    
    def __str__(self) -> str:
        return self.user.username
    @property
    def imageURL(self):
        try:
            url=self.Profile_img.url
        except:
            url=''
        return url


class Category(models.Model):
    name = models.CharField(max_length=100)
    description=models.CharField(max_length=250,blank=True,null=True)
    category_img=models.ImageField(upload_to='category_images',default='blank-profile-picture.png')

    def __str__(self):
        return self.name
    
    @property
    def imageURL(self):
        try:
            url=self.category_img.url
        except:
            url=''
        return url

class DiscussionThread(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    def create(self, title, creator):

        if not creator.has_perm('forum.create_thread'):
            raise PermissionDenied

        return super().create(title, creator)
    def __str__(self):
        return self.title

class Post(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4)
    title=models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    thread = models.ForeignKey(DiscussionThread, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    post_img=models.ImageField(upload_to='post_images',default='blank-profile-picture.png')
    
    @property
    def imageURL(self):
        try:
            url = self.post_img.url  
        except:
            url = ''
        return url
    
    def __str__(self):
        return self.content

class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return self.content
