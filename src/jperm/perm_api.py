# coding: utf-8

from .models import PermRule
from juser.models import (
    User,
    UserGroup,
)


def get_group_user_perm(obj):
    """
    获取用户或用户组授权的资产、资产组
    :param obj:用户或用户组
    :return:
    """

    perm = {}

    if isinstance(obj, User):
        rule_all = set(PermRule.objects.filter(user=obj))
        for user_group in obj.group.all():
            rule_all = rule_all.union(set(PermRule.objects.filter(user_group=user_group)))

    elif isinstance(obj, UserGroup):
        rule_all = set(PermRule.objects.filter(user_group=obj))

    else:
        rule_all = []

    perm['rule'] = rule_all
    perm_asset_group = perm['asset_group'] = {}
    perm_asset = perm['asset'] = {}
    perm_role = perm['role'] = {}
    for rule in rule_all:
        asset_groups = rule.asset_group.all()
        assets = rule.asset.all()
        perm_roles = rule.role.all()
        group_assets = []
        for asset_group in asset_groups:
            group_assets.extend(asset_group.asset_set.all())
        for role in perm_roles:
            if perm_role.get(role):
                perm_role[role]['asset'] = perm_role[role].get('asset', set()).union(set(assets).union(set(group_assets)))
                perm_role[role]['asset_group'] = perm_role.get('asset_group', set()).union(set(asset_groups))
            else:
                perm_role[role] = {'asset': set(assets).union(set(group_assets)), 'asset_group': set(asset_groups)}

        for asset in assets:
            if perm_asset[asset]:
                perm_asset[asset].get('role', set()).update(set(rule.role.all()))
                perm_asset[asset].get('rule', set()).add(rule)
            else:
                perm_asset[asset] = {'role':set(rule.role.all), 'rule': set([rule])}

        for asset_group in asset_groups:
            asset_group_assets = asset_group.asset_set.all()
            if perm_asset_group.get(asset_group):
                perm_asset_group[asset_group].get('role', set()).update(set(rule.role.all()))
                perm_asset_group[asset_group].get('rule', set()).add(rule)
            else:
                perm_asset_group[asset_group] = {'role': set(rule.role.all()), 'rule': set([rule]),
                                                 'asset': asset_group_assets}

            for asset in asset_group_assets:
                if perm_asset.get(asset):
                    perm_asset[asset].get('role', set()).update(perm_asset_group[asset_group].get('role', set()))
                    perm_asset[asset].get('rule', set()).update(perm_asset_group[asset_group].get('rule'), set())
                else:
                    perm_asset[asset] = {
                        'role': perm_asset_group[asset_group].get('role', set()),
                        'rule': perm_asset_group[asset_group].get('rule', set())
                    }
    return perm