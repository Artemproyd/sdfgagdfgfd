from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/<int:pk>/',
         views.PostDetailView.as_view(), name='post_detail'),
    path('category/<slug:category_slug>/',
         views.category,
         name='category_posts'),
    path('posts/create/',
         views.PostCreateView.as_view(),
         name='create_post'),
    path('posts/<int:pk>/edit/',
         views.PostUpdateView.as_view(),
         name='edit_post'),
    path('posts/<int:pk>/delete/',
         views.PostDeleteView.as_view(),
         name='delete_post'),
    path('profile/<slug:username>/',
         views.profile,
         name='profile'),
    path('prfile/edit/<slug:username>/',
         views.edit_profile,
         name='edit_profile'),
    path('<int:pk>/comment/',
         views.CommentCreateView.as_view(),
         name='add_comment'),
    path('posts/<int:cpk>/delete_comment/<int:pk>/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'),
    path('posts/<int:cpk>/edit_comment/<int:pk>/',
         views.CommentUpdateView.as_view(),
         name='edit_comment'),
]
