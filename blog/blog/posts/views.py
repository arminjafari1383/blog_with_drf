from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Category
from .serializers import *
from drf_spectacular.utils import extend_schema 
from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse,Http404
from .models import *
from .forms import *
# from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.views.generic import ListView,DetailView
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required



class CategoryViewSet(viewsets.ViewSet):
    queryset = Category.objects.all()
    
    @extend_schema(responses=CategorySerializer)
    def list(self, request):
        serializer = CategorySerializer(self.queryset,many = True)
        return Response(serializer.data)
    
class PostViewSet(viewsets.ViewSet):
    @extend_schema(responses=PostSerializer(many=True))
    def list(self, request):
        posts = Post.published.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)