from django.conf.urls import url
from views import *

urlpatterns = [
    url(r'^$', ArticleListView.as_view(), name = 'blog'),
    url(r'^article/publish', ArticlePublishView.as_view(), name='article_publish'),
#     url(r'^article/(?P<title>\S+)$', ArticleDetailView.as_view(), name='article_detail'),
    url(r'^article/(?P<title>\w+\.?\w+)$', ArticleDetailView.as_view(), name='article_detail'),
    url(r'^article/(?P<title>\w+\.?\w+)/edit$', ArticleEditView.as_view(), name='article_edit'),
]