from django.urls import path, include
from rest_framework_nested import routers
from .api import ForumPostViewSet, CommentViewSet

router = routers.SimpleRouter()
router.register(r'posts', ForumPostViewSet, basename='post')

posts_router = routers.NestedSimpleRouter(router, r'posts', lookup='post')
posts_router.register(r'comments', CommentViewSet, basename='post-comments')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(posts_router.urls)),
]
