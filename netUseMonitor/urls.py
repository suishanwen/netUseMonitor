"""netUseMonitor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path
from django.views.generic.base import RedirectView

from . import view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', view.hello),
    path('', view.index),
    path('add/', view.add),
    path('addCard/', view.addCard),
    path('update/', view.update),
    path('delete/', view.delete),
    path('query/', view.query),
    path('queryNet/', view.queryNet),
    path('emptyNetAll/', view.emptyNetAll),
    path('loadInfo/', view.loadInfo),
    path('voteInfo/', view.voteInfo),
    path('listVoteInfo/', view.list_vote_info),
    path('download/', view.download),
    path('listDownloads/', view.list_downloads),
    path('delDownload/', view.del_download),
    path('emptyDownloads/', view.empty_downloads),
    path('listOnline/', view.list_online),
    path("favicon.ico", RedirectView.as_view(url='netUseMonitor/favicon.ico')),
]
