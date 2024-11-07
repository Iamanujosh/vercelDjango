from django.contrib import admin

# Register your models here.
from .models import WardrobeItem,UserInfo

admin.site.register(WardrobeItem)
admin.site.register(UserInfo)
