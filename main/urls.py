from django.urls import path
from . import views

urlpatterns = [
    path('', views.PreviewList.as_view()),
]