from django.utils.safestring import mark_safe

from django.template import Library

import re

register = Library()

@register.inclusion_tag("menu.html")
def get_menu_styles(request):
    permission_menu_dict = request.session.get('permission_menu_dict')
    for val in permission_menu_dict.values():
        for item in val['children']:
            val['class'] = 'hide'
            if not hasattr(request,'show_id') or request.show_id==item['pk']:
                val['class'] = ''

    return {'permission_menu_dict':permission_menu_dict,'request':request}


@register.inclusion_tag("breadcrumb.html")
def breadcrumb(request):

    return {'breadcrumb_list': request.breadcrumb_list}



@register.simple_tag
def gen_role_url(request, rid):
    params = request.GET.copy()
    params._mutable = True
    params['rid'] = rid

    return params.urlencode()


@register.filter
def has_permission(btn_url,request):
    permission_names = request.session.get('permission_names')

    return btn_url in permission_names
