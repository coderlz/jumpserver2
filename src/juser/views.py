# coding: utf-8
from django.shortcuts import (
    render,
    get_object_or_404
)
from django.http import (
    HttpResponseRedirect,
    HttpResponse,
)
from django.core.urlresolvers import reverse
from django.db.models import Q
from .models import UserGroup
import datetime
import uuid
from jumpserver.api import pages
from .models import User
from jumpserver.api import (
    ServerError,
    PyCrypt,
)
from .user_api import (
    db_add_group,
    db_add_user,
    get_object,
    server_add_user,
    db_del_user,
    server_del_user,
    user_add_mail
)
from django.conf import settings
# Create your views here.


def group_add(request):
    """
    添加用户组
    :param request:
    :return:
    """
    header_title, path1, path2 = u'添加用户组', u'用户管理', u'添加用户组'
    error = ""
    msg = ""
    user_all = User.objects.all()

    if request.method == 'POST':
        group_name = request.POST.get('group_name', '')
        users_selected = request.POST.getlist('users_selected','')
        comment = request.POST.get('comment','')

        try:
            if not group_name:
                error = u'组名不能为空'
                raise ServerError(error)
            if UserGroup.objects.filter(name=group_name):
                error = u'组名已存在'
                raise ServerError(error)
            db_add_group(name=group_name, users_id=users_selected, comment=comment)
        except ServerError:
            pass
        except TypeError:
            error = u'添加组失败'
        else:
            msg = u'添加组 %s 成功' % group_name

    return render(request, 'juser/group_add.html', locals())


def group_list(request):
    header_title, path1, path2 = u'查看用户组', u'用户管理', u'查看用户组'
    keyword = request.GET.get('search', '')
    user_group_list = UserGroup.objects.all().order_by('name')
    group_id = request.GET.get('id','')

    if keyword:
        user_group_list = user_group_list.filter(Q(name__icontains=keyword) | Q(comment__icontains=keyword))

    if group_id:
        user_group_list = user_group_list.filter(id=int(group_id))

    user_group_list, p, user_groups, page_range, current_page, show_first, show_end = pages(user_group_list, request)

    return render(request, 'juser/group_list.html', context=locals())


def group_del(request):
    """
    删除用户组
    :param request:
    :return:
    """
    group_ids = request.GET.get('id')
    group_id_list = group_ids.split(',')
    for group_id in group_id_list:
        UserGroup.objects.filter(id=group_id).delete()

    return HttpResponse('删除成功')


def group_edit(request):
    header_title, path1, path2 = u'编辑用户组', u'用户管理', u'编辑用户组'
    error = ''
    msg = ''

    print 'Begin request'
    if request.method == 'GET':
        group_id = request.GET.get('id', '')
        user_group = get_object(UserGroup, id=group_id)
        print user_group
        users_selected = User.objects.filter(group=user_group)
        users_remain = User.objects.filter(~Q(group=user_group))
        users_all = User.objects.all()

    elif request.method == 'POST':
        group_id = request.POST.get('id', '')
        group_name = request.POST.get('group_name', '')
        users_selected = request.POST.getlist('users_selected', '')
        comment = request.POST.get('comment', '')

        try:
            if '' in [group_name, group_id]:
                error = u'组名不能为空'
                raise ServerError(error)
            if UserGroup.objects.filter(name=group_name).count() > 1:
                error = u'组名已存在'
                raise ServerError(error)
            db_add_group(name=group_name, users_id=users_selected, comment=comment)
            user_group = get_object_or_404(UserGroup, id=group_id)
            user_group.user_set.clear()
            for user in User.objects.filter(id__in=users_selected):
                user.group.add(UserGroup.objects.get(id=group_id))
            user_group.name = group_name
            user_group.comment = comment
            user_group.save()
        except ServerError, e:
            error = e

        if not error:
            return HttpResponseRedirect(reverse('juser:group_list'))
        else:
            users_all = User.objects.all()
            users_selected = User.objects.filter(group=user_group)
            users_remain = User.objects.filter(~Q(group=user_group))

    return render(request, 'juser/group_edit.html', context=locals())


def user_add(request):
    header_title, path1, path2 = u'添加用户', u'用户管理', u'添加用户'
    error = ""
    msg = ""
    user_role = {'SU': u'超级管理员', 'CU': u'普通用户'}
    group_all = UserGroup.objects.all()

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = PyCrypt.gen_rand_pass(16)
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        groups = request.POST.getlist('groups', [])
        admin_groups = request.POST.getlist('admin_groups', [])
        role = request.POST.get('role', 'CU')
        uuid_r = uuid.uuid4().get_hex()
        ssh_key_pwd = PyCrypt.gen_rand_pass(16)
        extra = request.POST.get('extra', '')
        is_active = False if '0' in extra else True
        send_mail_need = True if '1' in extra else False

        try:
            if '' in [username, password, ssh_key_pwd, name, role]:
                error= u'带*内容不能为空'
                raise ServerError
            check_user_is_exists = User.objects.filter(username=username)
            if check_user_is_exists:
                error = u'用户 %s 已存在' % username
                raise ServerError
        except ServerError:
            pass

        else:
            try:
                user = db_add_user(username=username, name=name, password=password,
                                   email=email,role=role,uuid=uuid_r,
                                   groups=groups,admin_groups=admin_groups,
                                   ssh_key_pwd=ssh_key_pwd, is_active=is_active,
                                   date_joined=datetime.datetime.now())

                server_add_user(username=username, ssh_key_pwd=ssh_key_pwd)
                user = get_object(User, username=username)
                if groups:
                    user_groups = []
                    for user_group_id in groups:
                        user_groups.extend(UserGroup.objects.filter(id=user_group_id))
            except IndexError, e:
                error = u'添加用户 %s 失败 %s' %(username, e)
                try:
                    db_del_user(username)
                    server_del_user(username)
                except Exception:
                    pass
            else:
                if settings.MAIL_ENABLE and send_mail_need:
                        user_add_mail(user, kwargs=locals())

    return render(request, 'juser/group_add.html', context=locals())


def user_list(request):
    header_title, path1, path2 = u'查看用户', u'用户管理', u'编辑用户组'
    user_role = {'SU': u'超级管理员', 'GA': u'组管理员', 'CU': u'普通用户'}
    keyword = request.GET.get('keyword', '')
    gid = request.GET.get('gid', '')
    users_list = User.objects.all().order_by('name')

    if gid:
        user_group = UserGroup.objects.filter(id=gid)
        if user_group:
            user_group = user_group.first()
            users_list = user_group.user_set.all()

    if keyword:
        users_list = users_list.filter(Q(name__icontains=keyword)).order_by('name')

    users_list, p, users, page_range, current_page, show_first, show_end = pages(users_list, request)

    return render(request, 'juser/user_list.html', context=locals())
