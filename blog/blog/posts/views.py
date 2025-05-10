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
from django.contrib.postgres.search import TrigramSimilarity
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import OpenApiParameter, extend_schema

    
class PostViewSet(viewsets.ViewSet):
    queryset = Post.published.all()  # اضافه شود
    lookup_field = 'pk'  # برای وضوح بیشتر

    @extend_schema(responses=PostSerializer(many=True))
    def list(self, request):
        posts = Post.published.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    @extend_schema(
        parameters=[OpenApiParameter(name='pk', type=int, location=OpenApiParameter.PATH)],
        responses=PostSerializer
    )
    def retrieve(self, request, pk=None):
        try:
            post = Post.published.get(pk=pk)
        except Post.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)
        
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


class PostSearchAPIView(APIView):
    @extend_schema(
        parameters=[],
        summary="جست و جو در پست ها",
        description = "جست و جو در عنوان و توضیحات پست ها با استفاده از trigramsimilarity",
        responses = {200:PostSerializer(many = True)}
    )
    def get (self,request):
        query = request.GET.get('query')
        if not query:
            return Response({"detail":"پارامتر 'query' مورد نیاز است."},status=status.HTTP_400_BAD_REQUEST)
        results_title = Post.published.annotate(
            similarity = TrigramSimilarity('title',query)
        ).filter(similarity__gt=0.1)

        results_desc = Post.published.annotate(
            similarity = TrigramSimilarity('description',query)
        ).filter(similarity__gt=0.1)

        results = (results_title | results_desc).distinct().order_by('-similarity')
        serializer = PostSerializer(results,many = True)
        return Response(serializer.data,status=200)
    
class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        summary = "نمایش پست کاربر جاری",
        description = "این api لیستی از پست هایی که کاربر احراز هویت شده منتشر کرده را برمی گرداند",
        responses = {200:PostSerializer(many = True)}
    )
    def get(self,request):
        user = request.user
        posts = Post.published.filter(author=user)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class CreatePostAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        request=CreatePostSerializer,
        responses={201: CreatePostSerializer},
        summary="ایجاد پست جدید با تصویر",
        description = "پستی جدید با دو تصویر برای کاربر لاگین شده ایجاد میکند "
    )
    def post(self, request):
        serializer = CreatePostSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save(author=request.user)
            return Response(CreatePostSerializer(post).data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class DeletePostAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        summary="حذف پست",
        description="پستی که متعلق به کاربر لاکین شده را حذف کند.",
        responses={204:None,403:{"detail":"اجازه ندارید."},404:{"detail":"یافت نشد."}} 
    )
    def delete(self,request,post_id):
        post = get_object_or_404(Post,id=post_id)
        
        if post.author != request.user:
            return Response({"detail":"شما اجازه حذف پست را ندارید."},status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class DeleteImageAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        summary = "حذف تصویر ",
        description="تصویری را که متعلق به پست کاربر فعلی است حذف میکند.",
        responses={204: None,403:{"detail":"اجازه ندارید."},404:{"detail":"یافت نشد."}}

    )
    def delete(self,request,image_id):
        image = get_object_or_404(Image, id=image_id)
        if image.post.author != request.user:
            return Response({"detail":"شما اجازه حذف تصویر را ندارید."},status=status.HTTP_403_FORBIDDEN)
        
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# views.py
class EditPostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UpdatePostSerializer,
        responses={200: UpdatePostSerializer},
        summary="ویرایش پست",
        description="ویرایش محتوای پستی که متعلق به کاربر فعلی است."
    )
    def put(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)

        if post.author != request.user:
            return Response({"detail": "شما اجازه ویرایش این پست را ندارید."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UpdatePostSerializer(post, data=request.data)
        if serializer.is_valid():
            updated_post = serializer.save()
            return Response(UpdatePostSerializer(updated_post).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterAPIView(APIView):
    @extend_schema(request=UserRegisterSerializer, responses={201: UserRegisterSerializer})
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserRegisterSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer