"""jumpserver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from .views import (
    group_list,
    group_add,
    group_edit,
    group_del,
    user_list,
    user_add,
    user_del,
    down_key,
    regen_ssh_key,
)

urlpatterns = [

    url(r'group/list/$', group_list, name='user_group_list'),
    url(r'group/add/$', group_add, name='user_group_add'),
    url(r'group/edit/$', group_edit, name='user_group_edit'),
    url(r'group/del/$', group_del, name='user_group_del'),
    url(r'user/list/$', user_list, name='user_list'),
    url(r'user/del/$', user_del, name='user_del'),
    url(r'user/add/$', user_add, name='user_add'),
    url(r'key/gen/$', regen_ssh_key, name='key_gen'),
    url(r'key/down/$', down_key, name='key_down'),

]
