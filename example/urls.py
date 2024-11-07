# urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('wardrobe/', views.user_wardrobe, name='wardrobe'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.register_view, name='signup'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('home/', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('add_clothes/', views.add_clothes, name='add_clothes'),
    path('sell/', views.sell, name='sell'),
    path('quiz/', views.user_quiz, name='user_quiz'),
    # path('vr/', views.vr, name='vr'),
]

# Add this to serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
