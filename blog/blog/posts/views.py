from django.shortcuts import render
from rest_framework import viewsets,status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from drf_spectacular.utils import extend_schema 
from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse,Http404
from .models import *
from .forms import *

    
class PostViewSet(viewsets.ViewSet):
    @extend_schema(responses=PostSerializer(many=True))
    def list(self, request):
        posts = Post.published.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    @extend_schema(responses=PostSerializer)
    def retrieve(self,request,pk = None):
        try:
            post = Post.published.get(pk=pk)
        except Post.DoesNotExist:
            return Response({"detail":"Not found."},status=404)
        
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
class TicketAPIView(APIView):
    @extend_schema(
            request = TicketSerializer,
            responses = {
                201:{"detail":"تیکت با موفقیت ثبت شد:"},
                400:{"detail":"درخواست نامعتبر بود"}

            },
            summary = "ثبت تیکت جدید",
            description = "این api برای ثبت تیکت جدید ایجاد میشود"
    )
    def post(self,request):
        serializer = TicketSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail":"تیکت با موفقیت ثبت شد."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors,status = status.HTTP_400_BAD_REQUEST)
    
class CommentAPIView(APIView):
    @extend_schema(
        request = CommentSerializer,
        responses={
            201:CommentSerializer,
            400:{"detail":"درخواست نامعتبر بود."}

        },
        summary = "ارسال نظر برای پست",
        description = "این API برای ارسال نظر جدید به یک پست منتشر شده استفاده می شود"
    )
    def post(self, request, post_id):
        post = Post.objects.filter(id=post_id, status=Post.Status.PUBLISHED).first()
        
        if not post:
            return Response(
                {"detail": "پست یافت نشد."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = CommentSerializer(data=request.data)
        
        if serializer.is_valid():
            comment = serializer.save(post=post)  # اضافه کردن نظر به پست
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)