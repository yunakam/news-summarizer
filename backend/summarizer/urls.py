from django.urls import path
from .views import summarize, extract_article

urlpatterns = [
    path("summarize/", summarize, name="summarize"),
    path("extract_article/", extract_article, name="extract_article"),
]
