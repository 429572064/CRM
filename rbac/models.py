from django.db import models
from employee.models import *


class Role(models.Model):
    """
    角色表
    """
    title = models.CharField(max_length=32)
    permissions = models.ManyToManyField('Permission')


    class Meta:
        app_label='rbac'


    def __str__(self):
        return self.title



class Permission(models.Model):
    """
    权限表
    """
    title = models.CharField(max_length=32)
    url = models.CharField(max_length=64)
    name = models.CharField(max_length=32,verbose_name='url别名')
    menu = models.ForeignKey('Menu',on_delete=models.CASCADE,null=True,blank=True)
    pid = models.ForeignKey('self',on_delete=models.CASCADE,null=True,verbose_name='父权限')

    class Meta:
        app_label='rbac'


    def __str__(self):
        return self.title


class User(models.Model):
    roles = models.ManyToManyField('Role')
    userinfo = models.OneToOneField('employee.UserInfo',on_delete=models.CASCADE)

    def __str__(self):
        return self.userinfo.username


class Menu(models.Model):
    title = models.CharField(max_length=32,verbose_name='菜单')
    icon = models.CharField(max_length=32,verbose_name='图标',null=True,blank=True)


    def __str__(self):
        return self.title