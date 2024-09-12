from django.urls import path,include
from .views import *

app_name="accounts"
# Create your views here.
urlpatterns = [
    path('profile/',profile_view, name='account_profile'),
    path('', include('allauth.urls')),  # Include allauth's URLs
]
