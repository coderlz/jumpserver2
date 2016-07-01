# coding:utf-8

from .models import (
    UserGroup,
    User,
    AdminGroup
)
from jumpserver.api import (
    get_object,
    bash,
    logger,
    mkdir,
    chown,

)
import os
from django.core.mail import send_mail
from django.conf import settings


def group_add_user(group, user_id=None, username=None):
    """
    用户组中添加用户
    :param group:
    :param user_id:
    :param username:
    :return:
    """
    if user_id:
        user = get_object(User, id=user_id)
    else:
        user = get_object(User, name=username)

    if user:
        group.user_set.add(user)


def db_add_group(**kwargs):
    """
    往数据库添加用户组
    :param kwargs:
    :return:
    """
    name = kwargs.get('name')
    group = get_object(UserGroup, name=name)
    users = kwargs.pop('users_id')

    if not group:
        group = UserGroup(**kwargs)
        group.save()
        for user_id in users:
            group_add_user(group, user_id)

def gen_ssh_key(username, password='',
                key_dir=os.path.join(settings.KEY_DIR, 'user'),
                authorized_keys=True, home="/home", length=2048):
    """
    生成用户ssh密匙对
    :param username:
    :param password:
    :param key_dir:
    :param authorized_keys:
    :param home:
    :param length:
    :return:
    """
    logger.debug('生成ssh_key,并设置authorized_keys')
    private_key_file = os.path.join(key_dir, username+'.perm')
    os.mkdir(key_dir, mode=777)
    if os.path.isfile(private_key_file):
        os.unlink(private_key_file)
    ret = bash('echo -e "y\n"|ssh-keygen -t rsa -f %s -b %s -P "%s"') % (private_key_file, length, password)

    if authorized_keys:
        auth_key_dir = os.path.join(home, username, '.ssh')
        mkdir(auth_key_dir, username=username, mode=700)
        authorized_key_file = os.path.join(auth_key_dir, 'authorized_keys')
        with open(private_key_file + '.pub') as pub_f:
            with open(authorized_key_file, 'w') as auth_f:
                auth_f.write(pub_f.read())
        os.chmod(authorized_key_file, mode=0600)
        chown(authorized_key_file, username)


def server_add_user(username, ssh_key_pwd=''):
    """
    在跳板机的服务器上添加一个用户
    :param username:
    :param ssh_key_pwd:
    :return:
    """
    bash("adduser -s '%s' '%s'") % (os.path.join(settings.BASE_DIR, 'init.sh'), username)
    gen_ssh_key(username, ssh_key_pwd)


def server_del_user(username):
    """
    删除系统上的用户
    :param username:
    :return:
    """
    bash('userdel -r -f %s' % username)
    logger.debug('rm -f %s/%s_*.perm' % (os.path.join(settings.KEY_DIR, 'user'), username))
    bash('rm -f %s/%s_*.perm' % (os.path.join(settings.KEY_DIR,'user'),username))


def db_add_user(**kwargs):
    """
    往数据库中添加用户
    :param kwargs:
    :return:
    """
    groups_post = kwargs.pop('groups')
    admin_groups = kwargs.pop('admin_groups')
    role = kwargs.get('role', 'CU')
    user = User(**kwargs)
    user.set_password(kwargs.get('password'))
    user.save()
    if groups_post:
        group_select = []
        for group_id in groups_post:
            group = UserGroup.objects.filter(id=group_id)
            group_select.extend(group)
        user.group = group_select

    if admin_groups and role == 'GA':
        for group_id in admin_groups:
            group = UserGroup.objects.filter(id=group_id)
            if group:
                AdminGroup(user=user, group=group).save()

    return user


def db_del_user(username):
    """
    从数据库删除用户
    :param username:
    :return:
    """
    user = get_object(User, username=username)
    if user:
        user.delete()


def user_add_mail(user, kwargs):
    """
    添加用户后，发送邮件给用户邮箱
    :param username:
    :return:
    """
    user_role = {'SU': u'超级管理员', 'GA': u'组管理员', 'CU': u'普通用户'}
    mail_title = u'恭喜你的跳板机用户 %s 添加成功 jumpserver' % user.name
    msg = u"""
    Hi %s:
        您的用户名: %s
        您的权限: %s
        您的web登陆密码: %s
        您的ssh密匙文件密码: %s
        密匙下载地址: %s/juser/key/down/?uuid=%s
        说明: 请登陆跳板机后台下载密匙, 然后使用密码登陆跳板机
    """ % (user.name, user.username, user_role.get(user.role, u'普通用户'),
           kwargs.get('password'), kwargs.get('ssh_key_pwd'), settings.URL, user.uuid)

    send_mail(mail_title, msg, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)