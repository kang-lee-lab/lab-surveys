from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("surveys/", include("surveys.urls")),  # For Heroku Production, frontend expects /surveys/*
    #path("", include("surveys.urls")),         # For Local Production, support root route
    path("admin/", admin.site.urls),
]
