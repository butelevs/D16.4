from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, article, news, Category, PostCategory, Author
from .filters import PostFilter
from .forms import PostForm
from django.shortcuts import redirect

from .tasks import notify_subscribers


class PostsList(ListView):
    model = Post
    ordering = '-create_time'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 2


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        return context


class PostSearch(ListView):
    model = Post
    ordering = '-create_time'
    template_name = 'search.html'
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_create.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        if not Author.objects.filter(user_id=self.request.user.id).exists():
            Author.objects.create(user_id=self.request.user.id)
        authors = Author.objects.filter(user_id=self.request.user.id)
        post.author = authors[0]

        if Post.objects.filter(author=authors[0]).exists():
            if len(Post.objects.filter(author=authors[0]).order_by('-create_time')) >= 3:
                ordered_posts = Post.objects.filter(author=authors[0]).order_by('-create_time')
                latest_post = Post.objects.filter(author=authors[0]).order_by('-create_time')[2]
            else:
                ordered_posts = Post.objects.filter(author=authors[0]).order_by('-create_time')
                latest_post = ordered_posts.last()
            latest_post_date = latest_post.create_time.strftime('%Y-%m-%d')
            if len(ordered_posts) >= 3 and latest_post_date == datetime.now().strftime('%Y-%m-%d'):
                return redirect('/')

        if 'articles' in self.request.path:
            post.type = article
        else:
            post.type = news
        post.save()
        notify_subscribers.apply_async([post.pk])
        # notify_subscribers.run(post.pk)
        return super().form_valid(form)


class PostUpdate(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_create.html'


class PostDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')


class Categories(ListView):
    model = Category
    template_name = 'categories.html'
    context_object_name = 'categories'


@login_required
def subscribe_to_category(request, pk):
    user = request.user
    chosen_cat = Category.objects.get(id=pk)

    if not chosen_cat.subscribers.filter(id=user.id).exists():
        chosen_cat.subscribers.add(user)

    return redirect('/')

# @login_required
# def unsubscribe_from_category(request, pk):
#     user = request.user
#     chosen_cat = Category.objects.get(id=pk)
#
#     if not chosen_cat.subscribers.filter(id=user.id).exists():
#         chosen_cat.subscribers.add(user)
#
#     return redirect('/')
