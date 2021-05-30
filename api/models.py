from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings

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



class Profile(models.Model):
  target_user = models.OneToOneField(
    settings.AUTH_USER_MODEL, related_name='target_user',
    on_delete=models.CASCADE
  )
  telephone_number = models.CharField(max_length=12, unique=True, blank=True)
  profile_name = models.CharField(max_length=100)
  profile_text = models.CharField(max_length=1000)
  is_college_student = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  profile_image = models.ImageField(blank=True, null=True, upload_to=upload_avatar_path)
  following_users = models.ManyToManyField(User, related_name='following_users',  blank=True)

  def __str__(self):
    return self.profile_name


class Post(models.Model):
  posted_user = models.ForeignKey(
    settings.AUTH_USER_MODEL, related_name='posted_user',
    on_delete=models.CASCADE
  )
  title = models.CharField(max_length=100)
  content = models.CharField(max_length=1000)
  post_image = models.ImageField(blank=True, null=True, upload_to=upload_post_path)
  is_published = models.BooleanField(default=False)
  published_at = models.DateTimeField(auto_now=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.title


class Review(models.Model):
  target_post = models.ForeignKey(
    Post, related_name='target_post',
    on_delete=models.CASCADE
  )
  review_text = models.CharField(max_length=1000)
  stars = models.PositiveSmallIntegerField()

  def __str__(self):
    return self.target_post.Post.title + self.review_text


class Message(models.Model):
  sender = models.ForeignKey(
    settings.AUTH_USER_MODEL, related_name='sender',
    on_delete=models.CASCADE
  )
  destination = models.ForeignKey(
    settings.AUTH_USER_MODEL, related_name='destination',
    on_delete=models.CASCADE
  )
  text = models.CharField(max_length=1000)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return str(self.sender) + ' -> ' + str(self.destination) + 'Text: ' + self.text

