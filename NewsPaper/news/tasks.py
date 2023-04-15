from celery import shared_task
import time

from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string

from django.contrib.auth.models import User
from .models import Post, article, news, Category, PostCategory
from datetime import datetime, timedelta


@shared_task
def hello():
    time.sleep(10)
    print("Hello, world!")


@shared_task
def notify_subscribers(pid):
    new_post = Post.objects.get(pk=pid)
    sub_users = new_post.category.all().values('subscribers__email')
    cats = new_post.category.all().values('name')
    print(new_post)
    print(sub_users)
    print(cats)

    sub_males = [sub['subscribers__email'] for sub in sub_users]
    cat_name = [cat['name'] for cat in cats]
    print(sub_males)
    print(cat_name)

    html_content = render_to_string(
        'post_for_send.html',
        {
            'post': new_post,
        }
    )

    msg = EmailMultiAlternatives(
        subject=f'{cat_name}: {new_post.heading}',
        body=new_post.text,
        from_email='lion4652@yandex.ru',
        to=sub_males,
    )
    msg.attach_alternative(html_content, "text/html")

    msg.send()


@shared_task
def weak_mailing():
    all_cats = Category.objects.all()
    print(all_cats)
    for cat in all_cats:
        cats_subs = Category.objects.filter(name=cat.name).values('subscribers__email')
        sub_males = [sub['subscribers__email'] for sub in cats_subs]

        today = datetime.now()
        seven_day_before = today - timedelta(days=7)
        all_posts = Post.objects.filter(category=cat, create_time__gte=seven_day_before)

        html_content = render_to_string(
            'posts_for_dispatch.html',
            {
                'post': all_posts,
                'cat_name': cat.name,
            }
        )

        msg = EmailMultiAlternatives(
            subject=f'Новости в категории: {cat.name}',
            from_email='lion4652@yandex.ru',
            to=sub_males,
        )
        msg.attach_alternative(html_content, "text/html")

        msg.send()