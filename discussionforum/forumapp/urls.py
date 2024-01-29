from django.urls import path
from . import views


urlpatterns = [
    path('signup',views.signup,name='signup'),
    path('signin',views.signin,name='signin'),
    path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',  
        views.activate, name='activate'), 
    path('',views.home,name="home"),
    path('logout',views.logout,name="logout"),
    path('posts/<str:category>/', views.posts_by_category, name="posts_by_category"),
    path('posts/detail/<str:pk>', views.detail, name="detail"),
    path('upload',views.upload_post,name="upload_post"),
]
