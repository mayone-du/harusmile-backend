# Generated by Django 3.2.3 on 2021-06-11 09:24

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_remove_profile_entry_talk_rooms'),
    ]

    operations = [
        migrations.AddField(
            model_name='talkroom',
            name='join_users',
            field=models.ManyToManyField(blank=True, default=[], related_name='join_users', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Entry',
        ),
    ]