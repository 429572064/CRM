from rbac.models import Role



def initial_session(user,request):
    """
    功能: 将当前登录人的所有权限注入session中
    :param user: 当前登录人
    """
    permissions = Role.objects.filter(user__userinfo=user).values('permissions__pk',
                                                        'permissions__url',
                                                        'permissions__pid',
                                                        'permissions__pid__menu_id',
                                                        'permissions__pid__title',
                                                        'permissions__pid__url',
                                                        'permissions__title',
                                                        'permissions__name',
                                                        'permissions__menu__title',
                                                        'permissions__menu__icon',
                                                        'permissions__menu__pk',
                                                        ).distinct()
    permission_list = []
    permission_names = []
    permission_menu_dict = {}

    for item in permissions:
        # 构建权限列表
        permission_list.append({
            'id':item['permissions__pk'],
            'url':item['permissions__url'],
            'pid':item['permissions__pid'],
            'pm_id':item['permissions__pid__menu_id'],
            'ptitle':item['permissions__pid__title'],
            'purl':item['permissions__pid__url'],
            'title':item['permissions__title'],
            'menu_id':item['permissions__menu__pk']
        })

        # 构建别名表.
        permission_names.append(item["permissions__name"])

        # 构建菜单权限
        menu_pk = item['permissions__menu__pk']
        if menu_pk:
            if menu_pk not in permission_menu_dict:
                permission_menu_dict[menu_pk] = {
                    'menu_id':item['permissions__menu__pk'],
                    'menu_title':item['permissions__menu__title'],
                    'menu_icon':item['permissions__menu__icon'],
                    'children':[{
                         'pk':item['permissions__pk'],
                         'url':item['permissions__url'],
                         'title':item['permissions__title'],
                    }]
                }
            else:
                permission_menu_dict[menu_pk]['children'].append({
                    'pk': item['permissions__pk'],
                    'url': item['permissions__url'],
                    'title': item['permissions__title'],
                })
    # 将当前登录人权限注入session表中
    request.session['permission_list'] = permission_list
    # 将当前登录人的权限别名注入到session表中
    request.session['permission_names'] = permission_names
    # 将当前登录人的菜单权限字典注入session表中
    request.session['permission_menu_dict'] = permission_menu_dict

