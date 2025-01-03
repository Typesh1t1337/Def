from django.urls import path
from .views import *

urlpatterns = [
    path('',IndexView.as_view(), name='index'),
    path('search/',SearchView.as_view(), name='search'),
    path('chat/<int:chat_id>/<str:nick>/', Message_view.as_view(), name='chat'),
]