from django.apps import AppConfig


class PostsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog.posts'

    def ready(self):
        import blog.posts.signals
