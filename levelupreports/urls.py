from django.urls import path
from .views import UserGameList
from .views import UserEventList

urlpatterns = [
    path('reports/usergames', UserGameList.as_view()),
    path('reports/userevents', UserEventList.as_view()),
]
