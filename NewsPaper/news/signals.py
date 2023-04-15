from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from django.contrib.auth.models import User

from .models import Post, article, news, Category, PostCategory


# @receiver(m2m_changed, sender=PostCategory)
# def notify_managers_appointment(sender, instance, action, **kwargs):
#     if action == 'post_add':
#         sub_users = instance.category.all().values('subscribers__email')
#         cats = instance.category.all().values('name')
#
#         sub_males = [sub['subscribers__email'] for sub in sub_users]
#         cat_name = [cat['name'] for cat in cats]
#
#         html_content = render_to_string(
#             'post_for_send.html',
#             {
#                 'post': instance,
#             }
#         )
#
#         msg = EmailMultiAlternatives(
#             subject=f'{cat_name}: {instance.heading}',
#             body=instance.text,
#             from_email='lion4652@yandex.ru',
#             to=sub_males,
#         )
#         msg.attach_alternative(html_content, "text/html")
#
#         msg.send()


@receiver(post_save, sender=User)
def welcome_send(sender, instance, created, **kwargs):

    if instance.is_active:
        send_mail(
            subject=f'Добро пожаловать {instance.username}!',
            message=f'Приветствуем Вас на нашем новостном портале!',
            from_email='lion4652@yandex.ru',
            recipient_list=[instance.email]
        )

