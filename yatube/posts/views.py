from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model

from .models import Post, Group
from .forms import PostForm

User = get_user_model()


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    total_posts = posts.count()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'total_posts': total_posts,
        'author': author
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    total_posts = Post.objects.filter(author=post.author).count()
    if request.user == post.author:
        is_author = True
    else:
        is_author = False
    context = {
        'post': post,
        'total_posts': total_posts,
        'is_author': is_author
    }
    return render(request, template, context)


def post_create(request):
    template = 'posts/create_post.html'
    if request.method == 'GET':
        form = PostForm()
        return render(request, template, {'form': form})
    form = PostForm(request.POST)
    if not form.is_valid():
        return render(request, template, {'form': form})
    form.instance.author = request.user
    form.save()
    return redirect('posts:profile', request.user.username)


def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = Post.objects.get(id=post_id)
    is_edit = True
    if request.method == 'GET':
        form = PostForm(instance=post)
        context = {
            'form': form,
            'is_edit': is_edit,
            'post': post
        }
        return render(request, template, context)
    form = PostForm(request.POST, instance=post)
    if not form.is_valid():
        return render(request, template, {'form': form})
    form.save()
    return redirect('posts:post_detail', post_id)
