# coding:utf-8
from django.shortcuts import render
from juser.models import User
from jlog.models import Log
from jasset.models import Asset
from jlog.models import Log
import datetime
from django.db.models import Count


def getDaysByNum(num):
    today = datetime.datetime.today()
    oneday = datetime.timedelta(days=1)
    date_li, date_str = [], []
    for i in range(0, num):
        today = today - oneday
        date_li.append(today)
        date_str.append(str(today)[5:10])

    date_li.reverse()
    date_str.reverse()
    return date_li, date_str


def get_data_by_day(date_li, item):
    data_li = []
    for d in date_li:
        logs = Log.objects.filter(start_time__year=d.year,
                                  start_time__month=d.month,
                                  start_time__day=d.day)
        if item == 'user':
            data_li.append(set([log.user for log in logs]))
        elif item == 'asset':
            data_li.append(set([log.host for log in logs]))
        elif item == 'login':
            data_li.append(logs)
        else:
            pass
    return data_li


def get_count_by_day(date_li, item):
    data_li = get_data_by_day(date_li, item)
    data_count_li = []
    for data in data_li:
        data_count_li.append(len(data))
    return data_count_li


def get_count_by_date(date_li, item):
    data_li = get_data_by_day(date_li, item)
    data_li_temp = []
    for data in data_li:
        data_li_temp.extend(list(data))

    return len(set(data_li_temp))


def index(request):
    # 准备数据
    li_date, li_str = getDaysByNum(7)
    today = datetime.datetime.now().day
    from_week = datetime.datetime.now() - datetime.timedelta(days=7)

    # dashboard 显示汇总
    users = User.objects.all()
    hosts = Asset.objects.all()
    online = Log.objects.filter(is_finished=0)
    online_host = online.values('host').distinct()
    online_user = online.values('user').distinct()
    active_users = User.objects.filter(is_active=1)
    active_hosts = Asset.objects.filter(is_active=1)

    # 一个月历史汇总
    date_li, date_str = getDaysByNum(30)
    date_month = repr(date_str)
    active_user_per_month = str(get_count_by_day(date_li, item='user'))
    active_asset_per_month = str(get_count_by_day(date_li, item='asset'))
    active_login_per_month = str(get_count_by_day(date_li, item='login'))

    # 活跃用户资产图
    active_user_month = get_count_by_date(date_li, item='user')
    disable_user_count = User.objects.filter(is_active=False).count()
    inactive_user_month = users.count() - disable_user_count
    active_asset_month = get_count_by_date(date_li, item='asset')
    disable_asset_month = hosts.filter(is_active=False).count() if hosts.filter(is_active=False) else 0
    inactive_asset_month = hosts.count() - disable_asset_month

    # 一周Top10用户和主机
    week_data = Log.objects.filter(start_time__range=[from_week, datetime.datetime.now()])
    user_top_10 = week_data.values('user').annotate(times=Count('user')).order_by('-times')[:10]
    host_top_10 = week_data.values('host').annotate(times=Count('host')).order_by('-times')[:10]

    for user_info in user_top_10:
        username = user_info.get('user')
        last = Log.objects.filter(user=username).latest('start_time')
        user_info['last'] = last

    for host_info in host_top_10:
        host = host_info.get('host')
        last = Log.objects.filter(host=host).latest('start_time')
        host_info['last'] = last

    # 一周Top5
    week_users = week_data.values('user').distinct().count()
    week_hosts = week_data.values('host').count()

    user_top_5 = week_data.values('user').annotate(times=Count('user')).order_by('-times')[:5]
    color = ['label-success', 'label-info', 'label-primary', 'label-default', 'label-warning']

    # 最后10次登陆
    login_10 = Log.objects.order_by('-start_time')[:10]
    login_10_more = Log.objects.order_by('-start_time')[10:21]

    return render(request, 'index.html', context=locals())
