from django.apps import AppConfig
import redis


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        import news.signals


red = redis.Redis(
    host='redis-15938.c9.us-east-1-4.ec2.cloud.redislabs.com',
    port=15938,
    password='e0Hu4vzIvkwBkhFqmAu1WPuqNvtuM4TV'
)
