# Generated by Django 3.2.3 on 2021-05-30 04:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20210530_1258'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='gender',
            field=models.CharField(choices=[('Male', '男性'), ('Female', '女性'), ('Others', 'その他')], default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='profile',
            name='address',
            field=models.CharField(choices=[('Hokkaido', '北海道'), ('Tokyo', '東京都'), ('Chiba', '千葉県')], max_length=50),
        ),
        migrations.AlterField(
            model_name='profile',
            name='profile_name',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='profile',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='tags', to='api.Tag'),
        ),
    ]
