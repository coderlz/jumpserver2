# coding: utf-8
from juser.models import (
    UserGroup,
    User,
)
from jperm.perm_api import (
    get_group_user_perm,
)
from django import template
from ..api import get_object
from django.conf import settings
import os


register = template.Library()


@register.filter(name='members_count')
def members_count(group_id):
    """
    统计用户组下成员数量
    :param group_id:
    :return:
    """
    group = get_object(UserGroup, id=group_id)
    if group:
        return group.user_set.count()
    else:
        return 0


@register.filter(name='groups2str')
def groups2str(grouplist):
    """
    将列表数组转化为str
    :param grouplist:
    :return:
    """
    if len(grouplist) < 3:
        return ''.join([group.name for group in grouplist])
    else:
        return '%s...' % (''.join([group.name for  group in grouplist[0:2]]))


@register.filter(name='get_role')
def get_role(user_id):
    """
    根据用户ID获取用户权限
    :param user_id:
    :return:
    """
    user_role = {'SU': u'超级管理员', 'GA': u'组管理员', 'CU': u'普通用户'}
    user = get_object(User, id=user_id)
    role = u'普通用户'
    if user:
        role = user_role.get(str(user.role), u'普通用户')
    return role


@register.filter(name='bool2str')
def bool2str(value):
    if value:
        return u'是'
    else:
        return u'否'


@register.filter(name='get_perm_asset_num')
def get_perm_asset_num(user_id):
    user = get_object(User, id=user_id)
    if user:
        user_perm_info = get_group_user_perm(user)
        return len(user_perm_info['asset'].keys())
    else:
        return 0


@register.filter(name='key_exists')
def key_exists(username):
    """
    检查ssh key是否在指定目录
    :param username:
    :return:
    """
    if os.path.isfile(os.path.join(settings.KEY_DIR, 'user', username + '.perm')):
        return True
    else:
        return False
