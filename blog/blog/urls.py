"""
URL configuration for blog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView,SpectacularSwaggerView
from blog.posts.views import *
from rest_framework_simplejwt.views import(
    TokenObtainPairView,
    TokenRefreshView,
)


router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
post_list = PostViewSet.as_view({'get': 'list'})
post_detail = PostViewSet.as_view({'get': 'retrieve'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/",include(router.urls)),
    path("api/ticket/", TicketAPIView.as_view(), name='ticket-api'),  # ثبت دستی مسیر برای Ticket
    path('api/posts/<int:post_id>/comment/', CommentAPIView.as_view(), name='comment-api'),
    path("api/posts/search",PostSearchAPIView.as_view(),name = 'post-search-api'),
    path("api/profile/",ProfileAPIView.as_view(),name = 'profile-api'),
    path("api/posts/create/",CreatePostAPIView.as_view(),name = "post-create-api"),
    path("api/posts/<int:post_id>/delete/",DeletePostAPIView.as_view(),name = 'post-delete-api'),
    path("api/images/<int:image_id>/delete/",DeleteImageAPIView.as_view(),name = 'image-delete-api'),
    path("api/posts/<int:post_id>/edit/", EditPostAPIView.as_view(), name="post-edit-api"),
    path("api/register/", RegisterAPIView.as_view(), name="user-register-api"),
    path("api/schema/",SpectacularAPIView.as_view(),name = "schema"),
    path("api/schema/docs/",SpectacularSwaggerView.as_view(url_name="schema")),
    path('posts/', post_list, name='post-list'),
    path('posts/<int:pk>/', post_detail, name='post-detail'),  # حتماً <int:pk>
    path('api/token/',TokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('api/token/refresh/',TokenRefreshView.as_view(),name='token_refresh'),
]
