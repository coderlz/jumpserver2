# coding:utf-8

from Crypto.Cipher import AES
import hashlib
import uuid
from binascii import a2b_hex,b2a_hex
import random
import subprocess
try:
    import pwd
except ImportError:
    pass
import os
import logging
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, InvalidPage


def set_log(level, filename='jumpserver.log'):
    """
    根据提示设置log打印
    :param level:
    :param filename:
    :return:
    """
    log_file = os.path.join(settings.LOG_DIR, filename)
    if not os.path.isfile(log_file):
        os.mknod(log_file)
        os.chmod(log_file, 0777)
    log_level_total = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARN,
        'error':logging.ERROR,
        'critical':logging.CRITICAL
    }
    logging_f = logging.getLogger('jumpserver')
    logging_f.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_file)
    fh.setLevel(log_level_total.get(level, logging.DEBUG))
    formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logging_f.addHandler(fh)
    return logging_f

def page_list_return(total, current=1):
    """
    返回本次分页的最小页数到最大页数列表
    :param total:
    :param current:
    :return:
    """
    min_page = current - 2 if current - 4 > 0 else 1
    max_page = min_page + 4 if min_page + 4 > total else total
    return range(min_page, max_page)


def pages(post_objects, request):
    """
    分页用公共函数,返回分页的对象元组
    :param post_objects:
    :param request:
    :return:
    """
    paginator = Paginator(post_objects, 20)
    try:
        current_page = int(request.GET.get('page', '1'))
    except:
        current_page = 1

    page_range = page_list_return(len(paginator.page_range), current_page)

    try:
        page_objects = paginator.page(current_page)
    except(EmptyPage, InvalidPage):
        page_objects = paginator.page(paginator.num_pages)

    if current_page >= 5:
        show_first = 1
    else:
        show_first = 0

    if current_page <= (len(paginator.page_range) - 3):
        show_end = 1
    else:
        show_end = 0

    return post_objects, paginator, page_objects, page_range, current_page, show_first, show_end


class ServerError(Exception):
    pass


def get_object(model, **kwargs):
    """
    封装函数查询数据库
    :param model:
    :param kwargs:
    :return:
    """

    for value in kwargs.values():
        if not value:
            return None

    the_object = model.objects.filter(**kwargs)
    if the_object.count() == 1:
        the_object = the_object.first()
    else:
        the_object = None
    return the_object


def chown(path, user, group=''):
    """
    修改路径的所有者
    :param dir_name:
    :param username:
    :param group:
    :return:
    """
    if not group:
        group = user

    try:
        uid = pwd.getpwnam(user).pw_uid
        gid = pwd.getpwnam(group).pw_gid
        os.chown(path, uid, gid)
    except KeyError:
        pass



def mkdir(dir_name, username='', mode=755):
    """
    目录如果不存在则创建，并赋予权限
    :param dir_name:
    :param username:
    :param mode:
    :return:
    """
    cmd = '[ -d %s ] && mkdir -p %s && chmod %s %s' %(dir_name, dir_name, mode, dir_name)
    bash(cmd)
    if username:
        chown(dir_name, username)


class PyCrypt(object):
    """
    用来加密的类
    """

    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC

    @staticmethod
    def gen_rand_pass(self, length=16, special=False):
        """
        随机生成密码
        :param self:
        :param length:
        :param special:
        :return:
        """
        salt_key = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
        symbol = '!@$%^&*()_'
        salt_lsit = []
        if special:
            for i in  range(length - 4):
                salt_lsit.append(random.choice(salt_key))
            for i in range(4):
                salt_lsit.append(random.choice(symbol))
        else:
            for i in range(length):
                salt_lsit.append(random.choice(salt_key))

        salt = ''.join(salt_lsit)
        return salt

    @staticmethod
    def md5_crypt(self, string):
        """
        MD5加密
        :param self:
        :param string:
        :return:
        """
        return hashlib.md5().update(string).hexdigest()

def bash(cmd):
    """
    执行bash命令
    :param cmd:
    :return:
    """
    subprocess.call(cmd, shell=True)


logger = set_log(settings.LOG_LEVEL)