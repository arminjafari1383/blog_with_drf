from rest_framework import serializers
from .models import Post,Ticket,Comment,Image
from django.contrib.auth.models import User


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title','description', 'slug', 'author', 'publish', 'status']

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['name','email','phone','subject','message']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['name','body']

class CreatePostSerializer(serializers.ModelSerializer):
    image1 = serializers.ImageField(write_only = True)
    image2 = serializers.ImageField(write_only = True)

    class Meta:
        model = Post
        fields = ['title','description','image1','image2']
    
    def create(self,validated_data):
        image1 = validated_data.pop('image1')
        image2 = validated_data.pop('image2')
        post = Post.objects.create(**validated_data)
        Image.objects.create(image_file=image1, post=post)
        Image.objects.create(image_file=image2, post=post)
        return post
    
# serializers.py
class UpdatePostSerializer(serializers.ModelSerializer):
    image1 = serializers.ImageField(write_only=True, required=False)
    image2 = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Post
        fields = ['title', 'description','image1', 'image2']  # یا هر فیلد دلخواه

    def update(self, instance, validated_data):
        image1 = validated_data.pop('image1', None)
        image2 = validated_data.pop('image2', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if image1:
            Image.objects.create(image_file=image1, post=instance)
        if image2:
            Image.objects.create(image_file=image2, post=instance)

        return instance

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user