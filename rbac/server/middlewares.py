from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse,redirect,render
import re


class PermissionMiddleWare(MiddlewareMixin):


    def process_request(self,request):
        current_path = request.path

        request.breadcrumb_list = [{'title': 'Home', 'url': '/index/'},]
        # 设置白名单放行
        white_list = ['/login/','/reg/','/index/','/get_auth_code/','/admin/.*','/rbac/permission_tree/']
        for url in white_list:
            ret = re.search(url,current_path)
            if ret:
                return None


        # 判断用户是否登录
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('/login/')


        # 面包屑列表
        request.breadcrumb_list = []
        # 权限判断
        permission_list = request.session.get('permission_list')
        for permission in permission_list:
            reg = '^%s$'%(permission['url'])
            if re.search(reg,current_path):
                pid = permission['pid']
                id = permission['id']
                ptitle = permission['ptitle']
                purl = permission['purl']
                pm_id = permission['pm_id']
                menu_id = permission['menu_id']
                request.show_id = pid or id
                if permission['url'] == '/index/':
                    request.breadcrumb_list = [{'title': 'Home', 'url': '/index/'}]
                    return
                if pid :
                    request.current_menu_id = pm_id
                    request.breadcrumb_list.extend(
                        [{'title':ptitle,'url':purl},
                         {'title':permission['title'],'url':permission['url']}]
                    )
                else:
                    request.current_menu_id = menu_id
                    request.breadcrumb_list.extend([{'title':permission['title'],'url':permission['url']}])

                return None
        return HttpResponse('没有访问权限!')

