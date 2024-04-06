from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.views.generic import (CreateView, DeleteView,
                                  DetailView, ListView, UpdateView)
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone

from .constants import PAGINATION_NUMBER
from .form import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post


def model_objects_filter(model_object):

    objects = model_object.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()).all()

    return objects


class PostMixin:
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        post_object = get_object_or_404(Post, pk=self.kwargs['pk'])
        if post_object.author == request.user:
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('blog:post_detail', **kwargs)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


def annotate_order(object):
    return object.order_by('-pub_date'
                           ).annotate(comment_count=Count('comments'))


class PostListView(ListView):
    template_name = 'blog/index.html'
    model = Post
    form_class = PostForm
    paginate_by = PAGINATION_NUMBER

    def get_queryset(self):
        context = model_objects_filter(super().get_queryset())
        return annotate_order(context)


class PostCreateView(LoginRequiredMixin,
                     CreateView):
    paginate_by = PAGINATION_NUMBER
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin,
                     PostMixin,
                     UpdateView):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin,
                     PostMixin,
                     DeleteView):
    ...


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    queryset = Post.objects.filter()

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, **kwargs):
        self.post = get_object_or_404(self.queryset, pk=self.kwargs['pk'])
        return self.post

    def get_context_data(self, **kwargs):
        if ((not self.post.category.is_published
                or not self.post.is_published)
                and str(self.post.author) != str(self.user.username)):
            raise Http404
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context

    def get_success_url(self):
        if not self.request.user.is_authenticated:
            return reverse('blog:post_detail', kwargs={'pk': self.object.id})
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


class CommentCreateView(LoginRequiredMixin, CreateView):
    post_object = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.post_object.pk})


class CommentMixin:
    comment_object = None
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.comment_object = get_object_or_404(Comment, pk=kwargs['pk'])
        if request.user != self.comment_object.author:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.comment_object.post_id})


class CommentDeleteView(LoginRequiredMixin,
                        CommentMixin,
                        DeleteView):
    ...


class CommentUpdateView(LoginRequiredMixin,
                        CommentMixin,
                        UpdateView):
    ...


def paginate_function(request, post_list):
    paginator = Paginator(post_list, PAGINATION_NUMBER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def category(request, category_slug):
    template = 'blog/category.html'
    category_object = get_object_or_404(Category,
                                        is_published=True,
                                        slug=category_slug)
    post_list = model_objects_filter(
        category_object.posts).order_by('-pub_date')

    context = {
        'category': category_object.title,
        'page_obj': paginate_function(request, post_list)
    }

    return render(request, template, context)


def profile(request, username=None):
    profile = get_object_or_404(User, username=username)
    if request.user == profile:
        post_list = profile.posts.filter().all()
    else:
        post_list = model_objects_filter(profile.posts)
    ready_post_list = annotate_order(post_list)
    context = {'profile': profile,
               'page_obj': paginate_function(request, ready_post_list)
               }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request, username=None):
    instance = get_object_or_404(User, username=username)
    if request.user != instance:
        raise Http404
    profile = ProfileForm(request.POST or None, instance=instance)
    context = {'form': profile}
    if profile.is_valid():
        profile.save()
    return render(request, 'blog/user.html', context)
