"""levelup URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from levelupapi.views import register_user, login_user
from levelupapi.views import GameTypeView
from levelupapi.views import EventView
from levelupapi.views import GameView


# the trailing_slash=False, will accept /gametypes rather then requiring /gametypes/
# the (r'gametypes') is stetting up the url, the GameTypeView is telling the server
# which view to use, and the third gametype, is the base name, which is a nickname
# if you get an error, and only uses the singular version
# same applies to event and game

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'gametypes', GameTypeView, 'gametype')
router.register(r'events', EventView, 'event')
router.register(r'games', GameView, 'game')

urlpatterns = [
    path('register', register_user),
    path('login', login_user),
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]
