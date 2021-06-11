# Generated by Django 3.2.3 on 2021-06-10 01:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_auto_20210610_1008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='admission_format',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='age',
            field=models.PositiveSmallIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='club_activities',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='department',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='favorite_subject',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='problem',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='undergraduate',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='want_hear',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
    ]