# Generated by Django 3.2.3 on 2021-06-11 08:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_auto_20210611_1339'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='entry_talk_rooms',
        ),
    ]