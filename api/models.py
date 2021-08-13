from datetime import time

from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models

# Create your models here.

# プロフィール用の画像のリネーム
def upload_avatar_path(instance, filename):
    # 拡張子を取得
    ext = filename.split('.')[-1]
    # ファイル名を変更して保存
    return '/'.join(['avatars', str(instance.target_user.id)+str(instance.profile_name)+str(".")+str(ext)])


# プラン用の画像のリネーム
def upload_plan_path(instance, filename):
    ext = filename.split('.')[-1]
    return '/'.join(['plans', str(instance.plan_author.id)+str(instance.title)+str(".")+str(ext)])


# Djangoのユーザーマネージャーを継承
class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('email is must')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    # スーパーユーザーの作成
    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# ユーザーモデル
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=50, unique=True)
    is_active = models.BooleanField(default=False)
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


# 手動で性別を追加
class Gender(models.Model):
    gender_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.gender_name

# 手動で47都道府県を登録する必要あり
class Address(models.Model):
    address_name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.address_name


# プロフィールモデル ユーザーとone-to-oneで紐付いている
class Profile(models.Model):
    target_user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='target_user',
        on_delete=models.CASCADE
    )
    telephone_number = models.CharField(
        max_length=11, unique=False, blank=True, null=True, default='')
    profile_name = models.CharField(max_length=100, default='')

    profile_text = models.CharField(
        max_length=1000, default='', blank=True, null=True)
    # 大学生か高校生可のフラグ
    is_college_student = models.BooleanField(default=False)
    # 通っている学校名
    school_name = models.CharField(
        max_length=100, default='', blank=True, null=True)
    # 作成日時
    created_at = models.DateTimeField(auto_now=True)
    # プロフィール画像
    profile_image = models.ImageField(
        blank=True, null=True, upload_to=upload_avatar_path)
    # 年齢
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

    # フォロー機能用（未実装）
    following_users = models.ManyToManyField(
        User, related_name='following_users',  blank=True, default=[])
    # 住所
    selected_address = models.ForeignKey(
        Address, related_name='selected_address',
        on_delete=models.PROTECT, blank=True, null=True
    )
    # 性別
    selected_gender = models.ForeignKey(
        Gender, related_name='selected_gender',
        on_delete=models.PROTECT, blank=True, null=True
    )
    tags = models.ManyToManyField(
        Tag, related_name='tags', blank=True, default=[])

    def __str__(self):
        return self.profile_name


# プランモデル
class Plan(models.Model):
    # プラン作成者
    plan_author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='plan_author',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=1000)
    plan_image = models.ImageField(
        blank=True, null=True, upload_to=upload_plan_path)
    # 公開フラグ
    is_published = models.BooleanField(default=False)
    # 公開日時
    published_at = models.DateTimeField(auto_now=True)
    # 作成日時
    created_at = models.DateTimeField(auto_now_add=True)
    # プランの料金
    price = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.plan_author.email + ' のプラン名 ' + self.title


# レビュー（ユーザーに対して　）
class Review(models.Model):
    # サービス提供者（大学生側）
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='provider',
        on_delete=models.CASCADE
    )
    # サービスを受けた側（高校生）
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='customer',
        on_delete=models.CASCADE
    )
    # レビューメッセージ
    review_text = models.CharField(max_length=1000)
    # レビューの評価（5段階の整数評価）
    stars = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.customer.target_user.profile_name + ' から ' + self.provider.target_user.profile_name + ' へ ' + '"' + self.review_text + '"'


# 通知
class Notification(models.Model):
    # 確認済みフラグ
    is_checked = models.BooleanField(default=False)
    # 通知者（メッセージを送信した側など）
    notificator = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='notificator',
        on_delete=models.CASCADE
    )
    # 通知を受け取った人
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='receiver',
        on_delete=models.CASCADE
    )
    # 通知の種類（メッセージ、レビュー...）
    notification_type = models.CharField(max_length=20)
    created_at = models.DateTimeField(
        auto_now_add=True)

    def __str__(self):
        return self.notificator.email + ' から ' + self.receiver.email + 'へ'


# トークルーム
class TalkRoom(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True)
    talk_room_description = models.CharField(
        max_length=300, default="", blank=True, null=True)

    # join_users = models.ManyToManyField(
    #     settings.AUTH_USER_MODEL, related_name='join_users',
    #     blank=True, default=[]
    # )

    # 紐付いているプラン ここからサービス提供者なども取得
    selected_plan = models.ForeignKey(
        Plan, related_name='selected_plan', on_delete=models.CASCADE,
        blank=True, null=True
    )

    # 相手のユーザー
    opponent_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='opponent_user',
        on_delete=models.CASCADE, blank=True, null=True
    )
    # 承認フラグ
    is_approve = models.BooleanField(default=False)

    def __str__(self):
        return str(self.talk_room_description)


# メッセージ
class Message(models.Model):
    # 紐付いているトークルーム
    talking_room = models.ForeignKey(
        TalkRoom, related_name='talking_room', on_delete=models.PROTECT
    )
    # 送信者
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='sender',
        on_delete=models.PROTECT
    )
    # 内容
    text = models.CharField(max_length=1000)
    is_viewed = models.BooleanField(default=False)
    # 相手がメッセージを確認したかどうか
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sender.target_user.profile_name + ' から ' + '"' + self.text + '"'
