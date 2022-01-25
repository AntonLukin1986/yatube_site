from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from posts import settings
from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Like, Post, User


def paginator(request, posts):
    paginator = Paginator(posts, settings.PAGINATOR_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    return render(request, 'posts/index.html', {
        'page_obj': paginator(
            request, Post.objects.select_related('author', 'group').all()
        )
    })


def groups_index(request):
    return render(
        request, 'posts/groups.html', {'groups': Group.objects.all()}
    )


def authors_index(request):
    users = User.objects.prefetch_related('posts').all()
    authors = [user for user in users if user.posts.exists()]
    return render(
        request,
        'posts/authors.html',
        {'authors': authors}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': paginator(request, group.posts.all())
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = (request.user.is_authenticated
                 and request.user != author
                 and Follow.objects.
                 filter(author=author, user=request.user).exists())
    return render(request, 'posts/profile.html', {
        'author': author,
        'following': following,
        'page_obj': paginator(request, author.posts.all())
    })


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    has_like = (request.user.is_authenticated
                and request.user != post.author
                and Like.objects.
                filter(post_id=post_id, user=request.user).exists())
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'has_like': has_like,
        'form': CommentForm()
    })


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES
    )
    if not form.is_valid():
        return render(request, 'posts/post_create.html', {'form': form})
    form.instance.author = request.user
    form.save()
    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        return render(
            request, 'posts/post_create.html', {'form': form, 'post': post}
        )
    form.save()
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        post = get_object_or_404(Post, id=post_id)
        form.instance.author = request.user
        form.instance.post = post
        form.save()
    return redirect('posts:post_detail', post_id)


@login_required
def follow_index(request):
    context = {
        'page_obj':
        paginator(
            request, Post.objects.filter(author__following__user=request.user)
        )
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if (request.user != author and not Follow.objects.
       filter(user=request.user, author=author).exists()):
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow, user=request.user, author__username=username
    ).delete()
    return redirect('posts:profile', username)


@login_required
def post_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if (request.user != post.author and not Like.objects.
       filter(user=request.user, post=post).exists()):
        Like.objects.create(user=request.user, post=post)
    return redirect('posts:post_detail', post_id)


@login_required
def post_unlike(request, post_id):
    get_object_or_404(
        Like, user=request.user, post__id=post_id
    ).delete()
    return redirect('posts:post_detail', post_id)
