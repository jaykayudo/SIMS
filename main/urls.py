from django.urls import path
from .views import *
urlpatterns = [
    path('',indexview,name = 'index'),
    path('about/',aboutview,name = 'about'),
    path('contact-us/',contactview,name = 'contact'),
    path('news',Events.as_view(),name = 'news'),
    path('news/<int:id>/',newsdetailview,name = 'news-detail'),
    path('login/',LoginView.as_view(),name = 'login')
]