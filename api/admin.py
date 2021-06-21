from django.contrib import admin

from .models import (Address, Gender, Message, Notification, Plan, Profile,
                     Review, Tag, TalkRoom, User)

# Register your models here.

admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Plan)
admin.site.register(Message)
admin.site.register(Review)
admin.site.register(Tag)
admin.site.register(Address)
admin.site.register(Gender)
admin.site.register(TalkRoom)
admin.site.register(Notification)
