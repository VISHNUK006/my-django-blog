from django.shortcuts import render, get_object_or_404, redirect
from .models import BlogPost, Comment, BlogImage, Category, Tag
from .forms import CommentForm
from django.db.models import Q 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import BlogPostForm
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from django.core.paginator import Paginator


def home(request):
    query = request.GET.get('q')
    if query:
        posts = BlogPost.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
    else:
        posts = BlogPost.objects.all()
    paginator = Paginator(posts.order_by('-created_at'), 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/home.html', {'posts': page_obj, 'page_obj': page_obj, 'filter_type': request.GET.get('filter_type'),
        'filter_name': request.GET.get('filter_name')})

def post_detail(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    comments = post.comments.all().order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()

            if post.author.email:
                send_mail(
                    subject=f"💬 New comment on your post: {post.title}",
                    message=f"{request.user.username} commented:\n\n{comment.content}",
                    from_email=None,
                    recipient_list=[post.author.email],
                    fail_silently=True,
                )

            return redirect('post_detail', post_id=post.id)
    else:
        form = CommentForm()

    return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments, 'form': form})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'blog/register.html', {'form': form})
@login_required
def create_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        files = request.FILES.getlist('images') 

        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.author = request.user
            blog_post.save()

            for f in files:
                BlogImage.objects.create(post=blog_post, image=f)

            return redirect('post_detail', post_id=blog_post.id)
    else:
        form = BlogPostForm()

    return render(request, 'blog/create_post.html', {
        'form': form
    })


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)

    if post.author != request.user:
        return HttpResponseForbidden("You are not allowed to edit this post.")

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = BlogPostForm(instance=post)

    return render(request, 'blog/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)

    if post.author != request.user:
        return HttpResponseForbidden("You are not allowed to delete this post.")

    if request.method == 'POST':
        post.delete()
        return redirect('home')

    return render(request, 'blog/delete_post.html', {'post': post})

@login_required
def my_posts(request):
    posts = BlogPost.objects.filter(author=request.user)
    return render(request, 'blog/my_posts.html', {'posts': posts})

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.user:
        return HttpResponseForbidden("You can't edit this comment.")

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('post_detail', post_id=comment.post.id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'blog/edit_comment.html', {'form': form, 'comment': comment})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.user:
        return HttpResponseForbidden("You can't delete this comment.")

    if request.method == 'POST':
        post_id = comment.post.id
        comment.delete()
        return redirect('post_detail', post_id=post_id)

    return render(request, 'blog/delete_comment.html', {'comment': comment})

@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    return redirect('post_detail', post_id=post.id)

def posts_by_category(request, category_name):
    posts = BlogPost.objects.filter(category__name=category_name)
    return render(request, 'blog/home.html', {'posts': posts, 'filter_type': 'Category', 'filter_name': category_name})

def posts_by_tag(request, tag_name):
    posts = BlogPost.objects.filter(tags__name=tag_name)
    return render(request, 'blog/home.html', {'posts': posts, 'filter_type': 'Tag', 'filter_name': tag_name})