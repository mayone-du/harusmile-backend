# Generated by Django 3.2.3 on 2021-06-07 13:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_auto_20210530_1921'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='reviewed_user',
        ),
        migrations.RemoveField(
            model_name='review',
            name='target_post',
        ),
        migrations.AddField(
            model_name='profile',
            name='age',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='review',
            name='customer',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='customer', to='api.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='review',
            name='provider',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='provider', to='api.user'),
            preserve_default=False,
        ),
    ]
