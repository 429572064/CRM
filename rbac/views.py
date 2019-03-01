from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse

from rbac.models import *


def permission_distribute(request):
    label = '权限分发'
    user_list = User.objects.all()
    role_list = Role.objects.all()
    uid = request.GET.get('uid')
    user = user_list.filter(id=uid).first()
    rid = request.GET.get('rid')
    role = role_list.filter(id=rid)

    if request.method == 'POST' and request.POST.get('postType') == 'role':
        list = request.POST.getlist('roles')
        print('role_list',role_list)
        user.roles.set(list)

    if request.method == 'POST' and request.POST.get('postType') == 'permission':
        list = request.POST.getlist('permission_id')
        role.first().permissions.set(list)

    if uid:
        role_id_list = user.roles.values_list('pk')
        role_id_list = [item[0] for item in role_id_list]
        if rid:
            per_id_list = role.values_list('permissions__pk').distinct()
        else:
            per_id_list = user.roles.values_list('permissions__pk').distinct()
        per_id_list = [item[0] for item in per_id_list]
    else:
        if rid:
            per_id_list = role.values_list('permissions__pk').distinct()
            per_id_list = [item[0] for item in per_id_list]

    return render(request,'permission_distribute.html',locals())


def permission_tree(request):

    permissions=Permission.objects.values("pk","title","url","menu__title","menu__pk","pid")

    return JsonResponse(list(permissions),safe=False)
