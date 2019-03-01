from django.urls import path, re_path
from rbac import views

urlpatterns = [
    path('distribute/',views.permission_distribute,name='permission_distribute'),
    path('permission_tree/',views.permission_tree,name='permission_tree'),

]