from datetime import time

from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models

# Create your models here.


def upload_avatar_path(instance, filename):
    ext = filename.split('.')[-1]
    return '/'.join(['avatars', str(instance.target_user.id)+str(instance.profile_name)+str(".")+str(ext)])


def upload_post_path(instance, filename):
    ext = filename.split('.')[-1]
    return '/'.join(['todos', str(instance.posted_user.id)+str(instance.title)+str(".")+str(ext)])


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('email is must')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    objects = UserManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email


class Tag(models.Model):
    tag_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.tag_name


class Gender(models.Model):
    gender_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.gender_name


class Address(models.Model):
    address_name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.address_name


class Profile(models.Model):
    target_user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='target_user',
        on_delete=models.CASCADE
    )
    telephone_number = models.CharField(
        max_length=11, unique=True, blank=True, default='')
    profile_name = models.CharField(max_length=100, default='')
    profile_text = models.CharField(max_length=1000, default='', blank=True)
    is_college_student = models.BooleanField(default=False)
    school_name = models.CharField(max_length=100, default='')
    created_at = models.DateTimeField(auto_now=True)
    profile_image = models.ImageField(
        blank=True, null=True, upload_to=upload_avatar_path)
    age = models.PositiveSmallIntegerField(default=0, blank=True, null=True)

    # 学部や学科（大学生用）
    undergraduate = models.CharField(
        max_length=100, default='', blank=True, null=True)
    department = models.CharField(
        max_length=100, default='', blank=True, null=True)
    club_activities = models.CharField(
        max_length=100, default='', blank=True, null=True)
    admission_format = models.CharField(
        max_length=100, default='', blank=True, null=True)
    favorite_subject = models.CharField(
        max_length=100, default='', blank=True, null=True)

    # 望んでほしいこと、悩み
    want_hear = models.CharField(
        max_length=100, default='', blank=True, null=True)
    problem = models.CharField(
        max_length=100, default='', blank=True, null=True)

    following_users = models.ManyToManyField(
        User, related_name='following_users',  blank=True, default=[])
    selected_address = models.ForeignKey(
        Address, related_name='selected_address',
        on_delete=models.PROTECT, blank=True
    )
    selected_gender = models.ForeignKey(
        Gender, related_name='selected_gender',
        on_delete=models.PROTECT, blank=True
    )
    tags = models.ManyToManyField(
        Tag, related_name='tags', blank=True, default=[])

    def __str__(self):
        return self.profile_name


class Plan(models.Model):
    plan_author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='plan_author',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=1000)
    plan_image = models.ImageField(
        blank=True, null=True, upload_to=upload_post_path)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.plan_author.email + ' のプラン名 ' + self.title


class Review(models.Model):
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='provider',
        on_delete=models.CASCADE
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='customer',
        on_delete=models.CASCADE
    )
    review_text = models.CharField(max_length=1000)
    stars = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.customer.target_user.profile_name + ' から ' + self.provider.target_user.profile_name + ' へ ' + '"' + self.review_text + '"'


class Notification(models.Model):
    is_checked = models.BooleanField(default=False)
    notificator = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='notificator',
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='receiver',
        on_delete=models.CASCADE
    )
    notification_type = models.CharField(max_length=20)
    created_at = models.DateTimeField(
        auto_now_add=True)

    def __str__(self):
        return self.notificator.email + ' から ' + self.receiver.email + 'へ'


class TalkRoom(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True)
    talk_room_description = models.CharField(
        max_length=300, default="", blank=True, null=True)

    # join_users = models.ManyToManyField(
    #     settings.AUTH_USER_MODEL, related_name='join_users',
    #     blank=True, default=[]
    # )

    selected_plan = models.ForeignKey(
        Plan, related_name='selected_plan', on_delete=models.CASCADE,
        blank=True, null=True
    )

    opponent_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='opponent_user',
        on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return str(self.talk_room_description)


class Message(models.Model):
    talking_room = models.ForeignKey(
        TalkRoom, related_name='talking_room', on_delete=models.PROTECT
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='sender',
        on_delete=models.PROTECT
    )
    text = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sender.target_user.profile_name + ' から ' + '"' + self.text + '"'
