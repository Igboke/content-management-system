from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import ArticleViewSet, CommentListCreateAPIView,CommentRetrieveUpdateDestroyAPIView, UserRegistrationAPIView, ArticleSearchView, ArticleSearchViewPro

article_list = ArticleViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
article_detail = ArticleViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

urlpatterns = [
    path("v1/user/create/",UserRegistrationAPIView.as_view(),name="create-user"),
    path("v1/articles/", article_list, name='article-list-create'),
    path("v1/articles/search/<str:name>/",ArticleSearchViewPro.as_view(),name="article-search-email"),
    path("v1/articles/search/", ArticleSearchView.as_view(),name="article-search"),
    path("v1/articles/<slug:slug>/",article_detail,name='article-detail'),
    path("v1/articles/<slug:slug>/comments/<int:pk>/",CommentRetrieveUpdateDestroyAPIView.as_view(),name="comment-list-create-update-delete"),
    path("v1/articles/<slug:slug>/comments/",CommentListCreateAPIView.as_view(),name="comment-list-create"),
    path("v1/auth/token/",obtain_auth_token,name="obtain-token")
]