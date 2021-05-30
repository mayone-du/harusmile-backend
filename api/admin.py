from django.contrib import admin
from .models import User, Profile, Post, Message, Review, Tag

# Register your models here.

admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Message)
admin.site.register(Review)
admin.site.register(Tag)