from django.urls import path
from .views import ArticleViewSet, CommentListCreateAPIView,CommentRetrieveUpdateDestroyAPIView

article_list = ArticleViewSet.as_view({
    'get': 'list'
})
article_detail = ArticleViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

urlpatterns = [
    path("v1/articles/", article_list, name='article-list'),
    path("v1/articles/<slug:slug>",article_detail,name='article-detail'),
    path("v1/articles/<slug:slug>/comments",CommentListCreateAPIView.as_view(),name="comment-list"),
    path("v1/articles/<slug:slug>/comments/<int:pk>/",CommentRetrieveUpdateDestroyAPIView.as_view(),name="comment-list-create-update-delete")
]