# coding: utf-8
from django.shortcuts import (
    render,
    render_to_response,
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
    is_role_request,
)
from .user_api import (
    db_add_group,
    db_add_user,
    db_update_user,
    get_object,
    server_add_user,
    db_del_user,
    server_del_user,
    user_add_mail,
    get_display_msg,
    gen_ssh_key,
    logger,
)
from django.conf import settings
from django.core.mail import send_mail
import os
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


def user_del(request):
    if request.method == 'GET':
        user_ids = request.GET.get('id', '')
        user_id_list = user_ids.split(',')
    elif request.method == 'POST':
        user_ids = request.POST.get('id', '')
        user_id_list = user_ids.split(',')
    else:
        return HttpResponse(u'错误请求')
    print request.POST.get('id')
    for user_id in user_id_list:
        user = get_object(User, id=user_id)
        if user and user.username != 'admin':
            logger.debug(u'删除用户 %s' % user.username)
            server_del_user(user.username)
            user.delete()
    return HttpResponse(u'删除成功',)


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
                msg = get_display_msg(user, password=password, ssh_key_pwd=ssh_key_pwd, send_mail_need=send_mail_need)

    return render(request, 'juser/user_add.html', context=locals())


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


def user_edit(request):
    header_title, path1, path2 = u'编辑用户', u'用户管理', u'编辑用户组'

    if request.method == 'GET':
        user_id = request.GET.get('id', '')
        if not user_id:
            HttpResponseRedirect(reverse('index'))

        user_role = {'SU': u'超级管理员', 'CU': u'普通用户'}
        user = get_object(User, id=user_id)
        group_all = UserGroup.objects.all()
        if user:
            groups_str = ' '.join([str(group.id) for group in user.group.all()])
            admin_groups_str = ' '.join([str(admin_group.group.id) for admin_group in user.admingroup_set.all()])
    else:
        user_id = request.GET.get('id', '')
        password = request.POST.get('password', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        role_post = request.POST.get('role', '')
        groups = request.POST.getlist('groups', '')
        admin_groups = request.POST.getlist('admin_groups', [])
        extra = request.POST.getlist('extra', [])
        is_active = True if '0' in extra else False
        email_need = True if '1' in extra else False
        user_role = {'SU': u'超级管理员', 'GA': u'组管理员', 'CU': u'普通用户'}

        if user_id:
            user = get_object(User, id=user_id)
        else:
            return HttpResponseRedirect(reverse('juser:user_list'))
        db_update_user(user_id=user_id,
                       password=password,
                       name=name,
                       email=email,
                       groups=groups,
                       admin_groups=admin_groups,
                       role=role_post,
                       is_active=is_active)
        if email_need:
            msg = u"""
            Hi %s:
                您的登录信息已修改，请登录跳板机查看信息
                地址: %s
                用户名: %s
                密码: %s(如果密码为None则代理原始密码)
                权限: %s

            """ % (user.name, settings.URL, user.username, password, user_role.get(role_post, u''))
            send_mail(u'您的信息已修改', msg, settings.EMAIL_HOST_USER, [email], fail_silently=False)
        return HttpResponseRedirect(reverse('juser:user_list'))
    return render(request, 'juser/user_edit.html', context=locals())


def regen_ssh_key(request):
    uuid_r = request.GET.get('uuid', '')
    user = get_object(User, uuid=uuid_r)
    if not user:
        return HttpResponse(u'没有该用户')

    username = user.username
    ssh_key_pass = PyCrypt.gen_rand_pass(16)
    gen_ssh_key(username, ssh_key_pass)
    return HttpResponse(u'密匙已经生产, 密码: %s,请到下载页面下载') % ssh_key_pass


def down_key(request):
    if is_role_request(request, 'super'):
        uuid_r = request.GET.get('uuid', '')
    else:
        uuid_r = request.user.uuid

    if uuid_r:
        user = get_object(User, uuid=uuid_r)
        if user:
            username = user.username
            private_key_file = os.path.join(settings.KEY_DIR, 'user', username + '.perm')
            if os.path.isfile(private_key_file):
                f = open(private_key_file)
                data = f.read()
                f.close()
                response = HttpResponse(data, content_type='applicaiton/octet-stream')
                response['Content-Disposition'] = 'attachment;file=%s' %(os.path.basename(private_key_file))
                if request.user.role == 'CU':
                    os.unlink(private_key_file)
                return response

    return HttpResponse('No Key File,Contact Admin')

