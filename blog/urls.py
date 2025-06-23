from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='blog/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
    path('create/', views.create_post, name='create_post'),
    path('edit/<int:post_id>/', views.edit_post, name='edit_post'),
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('post/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('category/<str:category_name>/', views.posts_by_category, name='posts_by_category'),
    path('tag/<str:tag_name>/', views.posts_by_tag, name='posts_by_tag'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
]

urlpatterns += [
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
]